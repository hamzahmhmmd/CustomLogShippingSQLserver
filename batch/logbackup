@REM this bat file connect to SQLDEV instance in localhost and execute log backup SP for LSDB database
sqlcmd -S .\SQLDEV -d LSDB -E -Q "EXEC dbo.PMAG_Backup @dbname = N'LSDB', @type = 'trn';"

@REM feelfree to add other database below for automatic backup using task scheduler
