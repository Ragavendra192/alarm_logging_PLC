-- Migration 002: Safe Creation of dbo.AlarmResponse
IF OBJECT_ID('dbo.AlarmResponse', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.AlarmResponse
    (
        Id BIGINT IDENTITY(1,1) PRIMARY KEY,
        MachineNumber VARCHAR(50) NOT NULL,
        AlarmCode VARCHAR(100) NOT NULL,
        AlarmDescription VARCHAR(500) NULL,
        AlarmStartTime DATETIME2 NOT NULL,
        AlarmEndTime DATETIME2 NULL,
        AlarmDurationSeconds INT NULL,
        Swift VARCHAR(100) NULL,
        RecipeName VARCHAR(200) NULL,
        OperatorName VARCHAR(200) NULL,
        MachineRunning BIT NULL,
        CycleRunning BIT NULL,
        MachineMode VARCHAR(50) NULL,
        HydraulicPressure REAL NULL,
        OilTemperature REAL NULL,
        Position REAL NULL,
        Force REAL NULL,
        InputList NVARCHAR(MAX) NULL,
        OutputList NVARCHAR(MAX) NULL,
        PLCConnected BIT NULL DEFAULT 1,
        OperatorAction NVARCHAR(1000) NULL,
        Resolution NVARCHAR(1000) NULL,
        CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    );
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_AlarmResponse_Machine_Start' AND object_id = OBJECT_ID('dbo.AlarmResponse'))
BEGIN
    CREATE INDEX IX_AlarmResponse_Machine_Start ON dbo.AlarmResponse(MachineNumber, AlarmStartTime DESC);
END
