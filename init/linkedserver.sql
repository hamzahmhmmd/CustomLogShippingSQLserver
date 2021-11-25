DECLARE @s NVARCHAR(128) = N'.\SQLLS1',
        @t NVARCHAR(128) = N'true',
        @p NVARCHAR(128) = N'MSOLEDBSQL',
        @i NVARCHAR(128) = N'10.10.10.12,1433';
EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'', @provider = @p,  @datasrc  = @i;
EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
GO

DECLARE @s NVARCHAR(128) = N'.\SQLLS2',
        @t NVARCHAR(128) = N'true',
        @p NVARCHAR(128) = N'MSOLEDBSQL',
        @i NVARCHAR(128) = N'10.10.10.12,1433';
EXEC [master].dbo.sp_addlinkedserver   @server     = @s, @srvproduct = N'', @provider = @p,  @datasrc  = @i;
EXEC [master].dbo.sp_addlinkedsrvlogin @rmtsrvname = @s, @useself = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'collation compatible', @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'data access',          @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc',                  @optvalue = @t;
EXEC [master].dbo.sp_serveroption      @server     = @s, @optname = N'rpc out',              @optvalue = @t;
