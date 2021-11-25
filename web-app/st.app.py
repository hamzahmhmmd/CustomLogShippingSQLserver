import os
import datetime
import pyodbc
import pymongo
import pandas as pd
import altair as alt
import streamlit as st
from collections import Counter

## streamlit page config
st.set_page_config(page_title='LS Dashboard monitoring', page_icon='😎', layout='wide', initial_sidebar_state='expanded', menu_items={'Get Help': None, 'Report a bug': None, 'About': None})

## connection string
# db LSDB
client = pymongo.MongoClient(**st.secrets["mongo"])

# get SQL server auth
@st.cache(ttl=600)
def get_data():
    db = client.logshipping
    items = db.lsdb.find()
    items = list(items)  # make hashable for st.cache
    return items

# _id, driver, server, instance_name, ls_database, trusted_connection = get_data()[2].values()
# windows_login = f'''\{instance_name} -d {ls_database} -E '''
# conn_str = (f'Driver={driver};Server={server}\{instance_name};Database={ls_database};Trusted_Connection={trusted_connection};')
# conn_str2 = (f'Driver=SQL Server;Server={server}\{instance_name};Database=rahasia;Trusted_Connection=yes;')


_id, driver, server, port, user, p4s5vv0rd, ls_database, trusted_connection = get_data()[3].values()
windows_login = f''',{port} -U {user} -P {p4s5vv0rd} -d {ls_database} '''  # aslinya pake pass and UID
conn_str = (f'Driver={driver};Server={server},{port};Database={ls_database};UID={user};PWD={p4s5vv0rd};Trusted_Connection=no')
conn_str2 = (f'Driver={driver};Server={server},{port};Database=rahasia;UID={user};PWD={p4s5vv0rd};Trusted_Connection=no;')

# df 2 csv
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
# return dataframe
def read2(conn_str, query):
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(list(row[0:len(columns)]))
    cnxn.close()
    df = pd.DataFrame(results, columns=columns)
    return df
# return dataframe
def read(conn_str, query):
    cnxn = pyodbc.connect(conn_str)
    return pd.read_sql_query(query, cnxn)
# void function
def write(conn_str, query):
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()
    with cnxn:
        cursor.execute(query)
    cnxn.close()
# format date time column
def format_datetime(x):
    return x.strftime("%m/%d/%Y %H:%M:%S")
# return folder size in MB
@st.cache(ttl=600)
def foldersizeMB(path):
    size = 0
    # path = path.replace('\\', "/")
    # path = path[:-1]

    # for ele in os.scandir(path):
    #     size += os.stat(ele).st_size

    return size/1000  # MB


## Pengambilan data
backupRestoreReport = read(conn_str=conn_str, query='SELECT * FROM PMAG_BackupRestoreReport')  # success backup view
# backupRestoreReport = backupRestoreReport[backupRestoreReport['Duration (millisecond)'] < 2000]
failBackupRestoreReport = read(conn_str=conn_str, query='SELECT * FROM PMAG_FailBackupRestoreReport')  # fail backup view
restoreReport = read(conn_str=conn_str, query='SELECT * FROM PMAG_LogRestoreHistory ORDER BY RestoreTime')  # for calculate last restore time and first restore time
activeSecondary = read(conn_str=conn_str, query="SELECT * FROM PMAG_ActiveSecondaries")  # view recent active sec. per db
secondariesFolder = read(conn_str=conn_str, query="SELECT DISTINCT ServerInstance, CommonFolder FROM PMAG_Secondaries")  # list of secondary instances
database = read(conn_str=conn_str, query="SELECT DatabaseName FROM PMAG_Databases")  # lis of db
db_instance = pd.merge(activeSecondary, secondariesFolder, on=['ServerInstance'])   # list db join list of instance folder
recent_backup_per_db = pd.merge(activeSecondary, backupRestoreReport.groupby(["Database"])["Backup Time"].max(), right_index=True, left_on='DatabaseName')
refresh = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

## sorting
backupRestoreReport = backupRestoreReport.sort_values(by='Backup Time').reset_index(drop=True)
failBackupRestoreReport = failBackupRestoreReport.sort_values(by='ID').reset_index(drop=True)

## Side Panel
with st.sidebar:
    # filter data
    with st.expander("⚙️ Apply filter to data", expanded=True):
        # form input
        col1, col2, col3 = st.columns([4, 4, 4])
        database_name = st.multiselect("Database", database['DatabaseName'].unique(), default=database['DatabaseName'].unique())
        serverInstanceList = [w.replace('.\\', '') for w in secondariesFolder['ServerInstance'].unique()]
        # backup_instances = st.multiselect("Backup Instances", secondariesFolder['ServerInstance'].unique(), default=secondariesFolder['ServerInstance'].unique())
        backup_instances = st.multiselect("Backup Instances", serverInstanceList, default=serverInstanceList)
        backup_instances = ['.\\' + w for w in backup_instances]
        # backup_instances
        date = st.date_input("Backup Date", value=[datetime.datetime.now() - datetime.timedelta(days=7), datetime.datetime.now()], max_value=datetime.datetime.now(), help="YYYY/MM/DD")
        # filter rules
        FilterApplied = (Counter(database_name) != Counter(database['DatabaseName'].unique())) \
            or (Counter(backup_instances) != Counter(secondariesFolder['ServerInstance'].unique())) \
            or (date != (datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()))
        # restore filter button
        if FilterApplied:
            if st.button('restore filter'):
                database_name = database['DatabaseName'].unique()
                backup_instances = secondariesFolder['ServerInstance'].unique()
                date = (datetime.date.today() - datetime.timedelta(days=7), datetime.date.today())
        # filter df backupRestoreReport
        backupRestoreReport = backupRestoreReport[(backupRestoreReport['Database'].isin(database_name))]  # filter db name
        backupRestoreReport = backupRestoreReport[(backupRestoreReport['Backup Server'].isin(backup_instances))]  # filter backup instances
        # filter date
        backupRestoreReport['Backup Date'] = pd.to_datetime(backupRestoreReport['Backup Date']).dt.date
        backupRestoreReport = backupRestoreReport[(backupRestoreReport['Backup Date'] >= date[0]) & (backupRestoreReport['Backup Date'] <= date[1])]
        # filter df failBackupRestoreReport
        failBackupRestoreReport = failBackupRestoreReport[(failBackupRestoreReport['Database'].isin(database_name))]  # filter db name
        failBackupRestoreReport = failBackupRestoreReport[(failBackupRestoreReport['Backup Server'].isin(backup_instances))]  # filter backup instances
        # filter date
        failBackupRestoreReport['Backup Date'] = pd.to_datetime(failBackupRestoreReport['Backup Date']).dt.date
        failBackupRestoreReport = failBackupRestoreReport[(failBackupRestoreReport['Backup Date'] >= date[0]) & (failBackupRestoreReport['Backup Date'] <= date[1])]
        # filter list of instance
        secondariesFolder = secondariesFolder[(secondariesFolder['ServerInstance'].isin(backup_instances))]
        # filter list of db
        activeSecondary = activeSecondary[(activeSecondary['DatabaseName'].isin(database_name))]

    # initiate new backup
    with st.expander("Initiate new backup"):
        with st.form(key='newbackup', clear_on_submit=True):
            db = st.text_input("Database", placeholder="exist database name", help=f'DB must exist in {server}/{port} instance')
            backup_instance = st.text_input("Backup instance", value="SQLSEC", help="makesure that instance connceted as server object")
            instance_commonfolder = st.text_input("Instance Folder", value="D:\SQLBackupsSEC\\", help="for storing backup & standby files")
            instance_datafolder = st.text_input("Data Folder", value=f'C:\Program Files\Microsoft SQL Server\MSSQL15.{backup_instance}\MSSQL\DATA\\')
            instance_LogFolder = st.text_input("Log Folder", value=f'C:\Program Files\Microsoft SQL Server\MSSQL15.{backup_instance}\MSSQL\DATA\\')
            submit = st.form_submit_button('Initialize backup')
            if submit:
                # cnxn2 = pyodbc.connect(conn_str_master)
                # cursor2 = cnxn2.cursor()
                # with cnxn2:
                #     cursor2.execute(f'''
                #     DECLARE
                #     @s NVARCHAR(128) = N'.\{backup_instance}',
                #     @t NVARCHAR(128) = N'true';
                #     EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'SQL Server';
                #     EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
                #     EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
                #     EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
                #     EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
                #     EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
                #     ''')
                cnxn = pyodbc.connect(conn_str)
                cursor = cnxn.cursor()
                with cnxn:
                    # set recovery full
                    cursor.execute(f'''
                    ALTER DATABASE {db} SET RECOVERY FULL;
                    ''')
                    # insert to PMAG_Databases
                    cursor.execute(f'''
                    INSERT dbo.PMAG_Databases(DatabaseName) SELECT N'{db}';
                    ''')
                    # insert to PMAG_Secondaries
                    cursor.execute(f'''
                    INSERT dbo.PMAG_Secondaries( DatabaseName, ServerInstance, CommonFolder, DataFolder, LogFolder, StandByLocation) 
                    SELECT DatabaseName = N'{db}', ServerInstance = name, CommonFolder = '{instance_commonfolder}', DataFolder = '{instance_datafolder}', LogFolder = '{instance_LogFolder}', StandByLocation = '{instance_commonfolder}' 
                    FROM sys.servers    
                    WHERE name LIKE N'.\{backup_instance}';
                    ''')
                os.system(f'''
                sqlcmd -S {server}{windows_login}-Q "EXEC dbo.PMAG_Backup @dbname = N'{db}', @type = 'bak', @init = 1;"
                ''')
                # success
                st.success('backup has been started')

    # manage backup manualy
    with st.expander("Trigger Backup and Delete", expanded=True):
        # go backup restore now
        st.subheader("run log shipping now")
        with st.form(key='lsnow', clear_on_submit=True):
            col1, col2 = st.columns([3, 2])
            db = col1.selectbox("Database", database['DatabaseName'].unique())
            tipe = col2.selectbox("backup type", options=['trn'])
            submit = st.form_submit_button('📬 start')
            if submit:
                os.system(f'''
                    sqlcmd -S {server}{windows_login}-Q "EXEC dbo.PMAG_Backup @dbname = N'{db}', @type = '{tipe}';"
                ''')
                # st.write(f'''sqlcmd -S {server}{windows_login}-Q "EXEC dbo.PMAG_Backup @dbname = N'{db}', @type = '{tipe}';"''')
                st.success('backup has been started')

        # go clear history
        st.subheader("Clear backup history")
        with st.form(key='clear', clear_on_submit=True):
            col1, col2 = st.columns([1.3, 1])
            db = col1.selectbox("Database", database['DatabaseName'].unique())
            dayold = col2.selectbox("days older than", [0, 1, 5, 7, 14, 30, 180, 360], index=2)
            # st.dataframe(db_instance['CommonFolder'][db_instance['DatabaseName'] == db])
            path = db_instance['CommonFolder'][db_instance['DatabaseName'] == db].item()
            delete_trn = st.checkbox("delete .trn files?", value=False, help='option for delete .trn files')

            submit = st.form_submit_button('🗑️ clear history')
            if submit:
                # os.system(f'cmd /c "clear-history.bat {dayold} {db} {path}"')
                os.system(f'''
                sqlcmd -S {server}{windows_login} -Q "EXEC dbo.PMAG_CleanupHistory @dbname = N'{db}', @DaysOld = {dayold};"
                ''')
                if delete_trn:
                    try:
                        for i in path.to_list():
                            os.system(f'''
                            forfiles /P {i} /S /M {db}*.trn* /D -{dayold} /C "cmd /c del @path"
                            ''')
                    except:
                        os.system(f'''
                        forfiles /P {path} /S /M {db}*.trn* /D -{dayold} /C "cmd /c del @path"
                        ''')
                st.success('deleted')

    # Insert tools (just for test)
    with st.expander("Add new record to DB rahasia"):
        ## add LastUpdate record
        st.subheader("add one record to table LastUpdate")
        with st.form(key='LastUpdate', clear_on_submit=True):
            submit = st.form_submit_button('⏱️ add current time')
            if submit:
                write(conn_str=conn_str2, query=f"INSERT LastUpdate(EventTime) SELECT SYSDATETIME()")
                st.success('new record has been added')
        ## add mahasiswa record
        st.subheader("add one record to table mahasiswa")
        with st.form(key='mahasiswa', clear_on_submit=True):
            nrp = st.number_input("nrp", min_value=0, step=1)
            nama = st.text_input("nama", placeholder='nama')
            submit = st.form_submit_button('+1 submit')
            if submit:
                write(conn_str=conn_str2, query=f"INSERT mahasiswa(nrp, nama) SELECT '{nrp}', '{nama}'")
                st.success('new record has been added')
            # else:
        ## read from standby server

## proses data
try:
    last = restoreReport['RestoreTime'].tail(1).item()
    first = restoreReport['RestoreTime'].head(1).item()
except:
    e = RuntimeError('Buat minimal satu log shipping backup')
    st.exception(e)
    st.subheader("run log shipping now")
    with st.form(key='lsnow2', clear_on_submit=True):
        col1, col2 = st.columns([3, 2])
        db = col1.selectbox("Database", database['DatabaseName'].unique())
        tipe = col2.selectbox("backup type", options=['trn'])
        submit = st.form_submit_button('📬 start')
        if submit:
            # os.system(f'cmd /c "ls.bat {db} {tipe}"')
            os.system(f'''
            sqlcmd -S {server}{windows_login} -Q "EXEC dbo.PMAG_Backup @dbname = N'{db}', @type = '{tipe}';"
            ''')
            st.success('backup has been started')
    st.stop()
n_backup = backupRestoreReport.shape[0]
n_fail = failBackupRestoreReport.shape[0]
avg = backupRestoreReport['Duration (millisecond)'].mean() / 1000
max = backupRestoreReport['Duration (millisecond)'].max() / 1000
secondariesFolder['Backup Folder Size (MB)'] = secondariesFolder['CommonFolder'].apply(foldersizeMB)
secondariesFolder.rename(columns={
    'ServerInstance': 'Backup Instance',
    'CommonFolder': 'Instance Folder'
}, inplace=True)
recent_backup_per_db['Last restore (minutes ago)'] = (datetime.datetime.now() - recent_backup_per_db['Backup Time']) / pd.Timedelta(minutes=1)
recent_backup_per_db['Last restore (minutes ago)'] = recent_backup_per_db['Last restore (minutes ago)'].map('{:.0f}'.format).map(int)
recent_backup_per_db['Last restore (minutes ago)'] = recent_backup_per_db['Last restore (minutes ago)']
recent_backup_per_db.rename(columns={
    'DatabaseName': 'Database',
    'ServerInstance': 'Standby Instance'
}, inplace=True)
backupRestoreReport['Backup Time'] = backupRestoreReport['Backup Time'].apply(lambda x: x.strftime("%m/%d/%Y %H:%M:%S"))

## Titile
with st.container():
    st.write("")
    st.title("📦 Log Shipping Backup Restore Report")
    col1, col2, col3, col4 = st.columns(4)
    # col1.caption(f'⏰ Data From Last **{-1 * ((first - datetime.datetime.now()).days)}** Days')
    col1.caption("🔄️ Last refresh __" + refresh + "__")
    # try:
    #     col2.caption(f'☁️instance: __{server}\{instance_name}__')
    # except:
    col2.caption(f'☁️instance: __{server},{port}__')
    col3.caption(f'🛢️ Database: __{ls_database}__')
    col4.caption(f'🕹️ press __ R __ for manual refresh')
    st.markdown('---')
    ## filter data
    if FilterApplied:
        st.info('filter applied')

## metric
with st.container():
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    # banyaknya backup
    col1.metric("# Success Backup", n_backup, 'backups')
    # jml backup yng tdk restore
    col2.metric("# Pending or Fail Restore", n_fail, 'backups')
    # kpn backup terakhir
    col3.metric("Last Backup", f'{((datetime.datetime.now() - last).total_seconds() / 60):.1f} min', 'ago')
    # next backup
    col4.metric("Next Backup in", f'{(((datetime.timedelta(minutes=15.0) + last) - datetime.datetime.now()).total_seconds()/60):.0f} min', 'automatic')
    # first backup (last delete)
    col5.metric("Last Clear History", f'{-1 * ((first - datetime.datetime.now()).days)} days', 'ago')
    # peek max durasi proses
    col6.metric("Avg process duration", f'{avg:.1f} sec', '1 sec')
    # avg durasi proses
    col7.metric("Longest process duration", f'{max:.1f} sec', '3 sec')
    # st.markdown("---")

## Last Restored secondary & backup instance storage
with st.container():
    col1, col2 = st.columns(2)
    col1.subheader('🛢️ Last Restored Secondary per DB') #
    col1.dataframe(recent_backup_per_db[['Database', 'Standby Instance', 'Last restore (minutes ago)']])
    col2.subheader('📁 Log file size per Instance')
    col2.dataframe(secondariesFolder)

## line chart monitor
with st.container():
    st.subheader('📈 Backup Restore Process in Millisecond')
    stat = backupRestoreReport[['Duration (millisecond)', 'Database']]

    stat.reset_index(inplace=True)
    c = alt.Chart(stat).mark_area(
        line={'color': '#5b8fc9'},
        color=alt.Gradient(gradient='linear',
                           stops=[alt.GradientStop(color='#162230', offset=0),
                                  alt.GradientStop(color='#5b8fc9', offset=1)],
                           x1=1, x2=1, y1=1, y2=0)
    ).encode(
        alt.X('index:Q', title=''),
        alt.Y('Duration (millisecond):Q', title='Process   (Millisecond)',
              # scale=alt.Scale(domain=[0, 1000])
              ),
        tooltip=['Duration (millisecond)', 'Database:N']
    ).interactive(bind_y=False).configure_axis(grid=True).configure_view(strokeWidth=0)
    st.altair_chart(c, use_container_width=True)

## data detail
with st.container():
    col1, col2 = st.columns(2)
    col1.subheader('✔️ Backup Restore Detailed Log')
    col2.subheader('❌ Pending or Failed Backup Restore Detailed Log')

    col1.dataframe(backupRestoreReport[['Database', 'Backup Server', 'Backup Time', 'File Location', 'Duration (millisecond)']], height=250)
    col2.dataframe(failBackupRestoreReport[['Database', 'Backup Server', 'Backup Time', 'File Location', 'Duration (millisecond)']], height=250)

    csv = convert_df(backupRestoreReport)
    col1.download_button(label="Download backup Restore Report as CSV",
                        data=csv,
                        file_name=f'backupRestoreReport-{datetime.datetime.now()}.csv',
                        mime='text/csv',)

## store snapshoot to mongodb
# snapshot = {
#     "timestamp": refresh,
#
# }

