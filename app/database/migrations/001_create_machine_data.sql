-- Migration 001: Safe Creation / Alter of dbo.MachineDataLog
-- Contains: Timestamp, OperatorName, Swift, 292 Boolean IO columns, 57 Press Real actuals
IF OBJECT_ID('dbo.MachineDataLog', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.MachineDataLog
    (
        Id BIGINT IDENTITY(1,1) PRIMARY KEY,
        MachineNumber VARCHAR(50) NOT NULL,
        [Timestamp] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        [Alarm] VARCHAR(500) NULL,
        OperatorName VARCHAR(200) NULL,
        Swift VARCHAR(100) NULL,

        [0.0] BIT NULL,
        [0.1] BIT NULL,
        [0.2] BIT NULL,
        [0.3] BIT NULL,
        [0.4] BIT NULL,
        [0.5] BIT NULL,
        [0.6] BIT NULL,
        [0.7] BIT NULL,
        [1.0] BIT NULL,
        [1.1] BIT NULL,
        [1.2] BIT NULL,
        [1.3] BIT NULL,
        [1.4] BIT NULL,
        [1.5] BIT NULL,
        [1.6] BIT NULL,
        [1.7] BIT NULL,
        [2.0] BIT NULL,
        [2.1] BIT NULL,
        [2.2] BIT NULL,
        [2.3] BIT NULL,
        [2.4] BIT NULL,
        [2.5] BIT NULL,
        [2.6] BIT NULL,
        [2.7] BIT NULL,
        [3.0] BIT NULL,
        [3.1] BIT NULL,
        [3.2] BIT NULL,
        [3.3] BIT NULL,
        [3.4] BIT NULL,
        [3.5] BIT NULL,
        [3.6] BIT NULL,
        [3.7] BIT NULL,
        [4.0] BIT NULL,
        [4.1] BIT NULL,
        [4.2] BIT NULL,
        [4.3] BIT NULL,
        [4.4] BIT NULL,
        [4.5] BIT NULL,
        [4.6] BIT NULL,
        [4.7] BIT NULL,
        [5.0] BIT NULL,
        [5.1] BIT NULL,
        [5.2] BIT NULL,
        [5.3] BIT NULL,
        [5.4] BIT NULL,
        [5.5] BIT NULL,
        [5.6] BIT NULL,
        [5.7] BIT NULL,
        [6.0] BIT NULL,
        [6.1] BIT NULL,
        [6.2] BIT NULL,
        [6.3] BIT NULL,
        [6.4] BIT NULL,
        [6.5] BIT NULL,
        [6.6] BIT NULL,
        [6.7] BIT NULL,
        [7.0] BIT NULL,
        [7.1] BIT NULL,
        [7.2] BIT NULL,
        [7.3] BIT NULL,
        [7.4] BIT NULL,
        [7.5] BIT NULL,
        [7.6] BIT NULL,
        [7.7] BIT NULL,
        [8.0] BIT NULL,
        [8.1] BIT NULL,
        [8.2] BIT NULL,
        [8.3] BIT NULL,
        [8.4] BIT NULL,
        [8.5] BIT NULL,
        [8.6] BIT NULL,
        [8.7] BIT NULL,
        [9.0] BIT NULL,
        [9.1] BIT NULL,
        [9.2] BIT NULL,
        [9.3] BIT NULL,
        [9.4] BIT NULL,
        [9.5] BIT NULL,
        [9.6] BIT NULL,
        [9.7] BIT NULL,
        [10.0] BIT NULL,
        [10.1] BIT NULL,
        [10.2] BIT NULL,
        [10.3] BIT NULL,
        [10.4] BIT NULL,
        [10.5] BIT NULL,
        [10.6] BIT NULL,
        [10.7] BIT NULL,
        [11.0] BIT NULL,
        [11.1] BIT NULL,
        [11.2] BIT NULL,
        [11.3] BIT NULL,
        [11.4] BIT NULL,
        [11.5] BIT NULL,
        [11.6] BIT NULL,
        [11.7] BIT NULL,
        [12.0] BIT NULL,
        [12.1] BIT NULL,
        [12.2] BIT NULL,
        [12.3] BIT NULL,
        [12.4] BIT NULL,
        [12.5] BIT NULL,
        [12.6] BIT NULL,
        [12.7] BIT NULL,
        [13.0] BIT NULL,
        [13.1] BIT NULL,
        [13.2] BIT NULL,
        [13.3] BIT NULL,
        [13.4] BIT NULL,
        [13.5] BIT NULL,
        [13.6] BIT NULL,
        [13.7] BIT NULL,
        [14.0] BIT NULL,
        [14.1] BIT NULL,
        [14.2] BIT NULL,
        [14.3] BIT NULL,
        [14.4] BIT NULL,
        [14.5] BIT NULL,
        [14.6] BIT NULL,
        [14.7] BIT NULL,
        [15.0] BIT NULL,
        [15.1] BIT NULL,
        [15.2] BIT NULL,
        [15.3] BIT NULL,
        [15.4] BIT NULL,
        [15.5] BIT NULL,
        [15.6] BIT NULL,
        [15.7] BIT NULL,
        [16.0] BIT NULL,
        [16.1] BIT NULL,
        [16.2] BIT NULL,
        [16.3] BIT NULL,
        [16.4] BIT NULL,
        [16.5] BIT NULL,
        [16.6] BIT NULL,
        [16.7] BIT NULL,
        [17.0] BIT NULL,
        [17.1] BIT NULL,
        [17.2] BIT NULL,
        [17.3] BIT NULL,
        [17.4] BIT NULL,
        [17.5] BIT NULL,
        [17.6] BIT NULL,
        [17.7] BIT NULL,
        [18.0] BIT NULL,
        [18.1] BIT NULL,
        [18.2] BIT NULL,
        [18.3] BIT NULL,
        [18.4] BIT NULL,
        [18.5] BIT NULL,
        [18.6] BIT NULL,
        [18.7] BIT NULL,
        [19.0] BIT NULL,
        [19.1] BIT NULL,
        [19.2] BIT NULL,
        [19.3] BIT NULL,
        [19.4] BIT NULL,
        [19.5] BIT NULL,
        [19.6] BIT NULL,
        [19.7] BIT NULL,
        [20.0] BIT NULL,
        [20.1] BIT NULL,
        [20.2] BIT NULL,
        [20.3] BIT NULL,
        [20.4] BIT NULL,
        [20.5] BIT NULL,
        [20.6] BIT NULL,
        [20.7] BIT NULL,
        [21.0] BIT NULL,
        [21.1] BIT NULL,
        [21.2] BIT NULL,
        [21.3] BIT NULL,
        [21.4] BIT NULL,
        [21.5] BIT NULL,
        [21.6] BIT NULL,
        [21.7] BIT NULL,
        [22.0] BIT NULL,
        [22.1] BIT NULL,
        [22.2] BIT NULL,
        [22.3] BIT NULL,
        [22.4] BIT NULL,
        [22.5] BIT NULL,
        [22.6] BIT NULL,
        [22.7] BIT NULL,
        [23.0] BIT NULL,
        [23.1] BIT NULL,
        [23.2] BIT NULL,
        [23.3] BIT NULL,
        [23.4] BIT NULL,
        [23.5] BIT NULL,
        [23.6] BIT NULL,
        [23.7] BIT NULL,
        [24.0] BIT NULL,
        [24.1] BIT NULL,
        [24.2] BIT NULL,
        [24.3] BIT NULL,
        [24.4] BIT NULL,
        [24.5] BIT NULL,
        [24.6] BIT NULL,
        [24.7] BIT NULL,
        [25.0] BIT NULL,
        [25.1] BIT NULL,
        [25.2] BIT NULL,
        [25.3] BIT NULL,
        [25.4] BIT NULL,
        [25.5] BIT NULL,
        [25.6] BIT NULL,
        [25.7] BIT NULL,
        [26.0] BIT NULL,
        [26.1] BIT NULL,
        [26.2] BIT NULL,
        [26.3] BIT NULL,
        [26.4] BIT NULL,
        [26.5] BIT NULL,
        [26.6] BIT NULL,
        [26.7] BIT NULL,
        [27.0] BIT NULL,
        [27.1] BIT NULL,
        [27.2] BIT NULL,
        [27.3] BIT NULL,
        [27.4] BIT NULL,
        [27.5] BIT NULL,
        [27.6] BIT NULL,
        [27.7] BIT NULL,
        [28.0] BIT NULL,
        [28.1] BIT NULL,
        [28.2] BIT NULL,
        [28.3] BIT NULL,
        [28.4] BIT NULL,
        [28.5] BIT NULL,
        [28.6] BIT NULL,
        [28.7] BIT NULL,
        [29.0] BIT NULL,
        [29.1] BIT NULL,
        [29.2] BIT NULL,
        [29.3] BIT NULL,
        [29.4] BIT NULL,
        [29.5] BIT NULL,
        [29.6] BIT NULL,
        [29.7] BIT NULL,
        [30.0] BIT NULL,
        [30.1] BIT NULL,
        [30.2] BIT NULL,
        [30.3] BIT NULL,
        [30.4] BIT NULL,
        [30.5] BIT NULL,
        [30.6] BIT NULL,
        [30.7] BIT NULL,
        [31.0] BIT NULL,
        [31.1] BIT NULL,
        [31.2] BIT NULL,
        [31.3] BIT NULL,
        [31.4] BIT NULL,
        [31.5] BIT NULL,
        [31.6] BIT NULL,
        [31.7] BIT NULL,
        [32.0] BIT NULL,
        [32.1] BIT NULL,
        [32.2] BIT NULL,
        [32.3] BIT NULL,
        [32.4] BIT NULL,
        [32.5] BIT NULL,
        [32.6] BIT NULL,
        [32.7] BIT NULL,
        [33.0] BIT NULL,
        [33.1] BIT NULL,
        [33.2] BIT NULL,
        [33.3] BIT NULL,
        [33.4] BIT NULL,
        [33.5] BIT NULL,
        [33.6] BIT NULL,
        [33.7] BIT NULL,
        [34.0] BIT NULL,
        [34.1] BIT NULL,
        [34.2] BIT NULL,
        [34.3] BIT NULL,
        [34.4] BIT NULL,
        [34.5] BIT NULL,
        [34.6] BIT NULL,
        [34.7] BIT NULL,
        [35.0] BIT NULL,
        [35.1] BIT NULL,
        [35.2] BIT NULL,
        [35.3] BIT NULL,
        [35.4] BIT NULL,
        [35.5] BIT NULL,
        [35.6] BIT NULL,
        [35.7] BIT NULL,
        [36.0] BIT NULL,
        [36.1] BIT NULL,
        [36.2] BIT NULL,
        [36.3] BIT NULL,
        [P1 MAIN RAM PRESSURE] REAL NULL,
        [P1 MAIN RAM POSITION] REAL NULL,
        [P1 DIECUSHION PRESSURE] REAL NULL,
        [P1 DIECUSHION POSITION] REAL NULL,
        [P1 DAMPUR PRESSURE] REAL NULL,
        [P1 OIL LVEL LOW] REAL NULL,
        [P1 OIL TEMP HIGH] REAL NULL,
        [P1 CYCLE TIME] REAL NULL,
        [P1 DWELL TIME] REAL NULL,
        [P1 PRV.CYCLE TIME] REAL NULL,
        [P1 SHIFT COUNT] REAL NULL,
        [P1 CUMM COUNT] REAL NULL,
        [P1 MACHINE LIFE COUNT] REAL NULL,
        [P1 MAIN RAM TONNAGE] REAL NULL,
        [P1 DC TONNAGE] REAL NULL,
        [P1 PUMP 1 PRESSURE TRANSDUCER] REAL NULL,
        [P1 PUMP 2 PRESSURE TRANSDUCER] REAL NULL,
        [P1 PUMP 3 PRESSURE TRANSDUCER] REAL NULL,
        [P1 MAIN RAM B-LINE PRESSURE TRANSDUCER] REAL NULL,
        [P2 MAIN RAM PRESSURE] REAL NULL,
        [P2 MAIN RAM POSITION] REAL NULL,
        [P2 DIECUSHION PRESSURE] REAL NULL,
        [P2 DIECUSHION POSITION] REAL NULL,
        [P2 DAMPUR PRESSURE] REAL NULL,
        [P2 OIL LVEL LOW] REAL NULL,
        [P2 OIL TEMP HIGH] REAL NULL,
        [P2 CYCLE TIME] REAL NULL,
        [P2 DWELL TIME] REAL NULL,
        [P2 PRV.CYCLE TIME] REAL NULL,
        [P2 SHIFT COUNT] REAL NULL,
        [P2 CUMM COUNT] REAL NULL,
        [P2 MACHINE LIFE COUNT] REAL NULL,
        [P2 MAIN RAM TONNAGE] REAL NULL,
        [P2 DC TONNAGE] REAL NULL,
        [P2 PUMP 4 PRESSURE TRANSDUCER] REAL NULL,
        [P2 PUMP 5 PRESSURE TRANSDUCER] REAL NULL,
        [P2 PUMP 6 PRESSURE TRANSDUCER] REAL NULL,
        [P2 MAIN RAM B-LINE PRESSURE TRANSDUCER] REAL NULL,
        [P3 MAIN RAM PRESSURE] REAL NULL,
        [P3 MAIN RAM POSITION] REAL NULL,
        [P3 DIECUSHION PRESSURE] REAL NULL,
        [P3 DIECUSHION POSITION] REAL NULL,
        [P3 DAMPUR PRESSURE] REAL NULL,
        [P3 OIL LVEL LOW] REAL NULL,
        [P3 OIL TEMP HIGH] REAL NULL,
        [P3 CYCLE TIME] REAL NULL,
        [P3 DWELL TIME] REAL NULL,
        [P3 PRV.CYCLE TIME] REAL NULL,
        [P3 SHIFT COUNT] REAL NULL,
        [P3 CUMM COUNT] REAL NULL,
        [P3 MACHINE LIFE COUNT] REAL NULL,
        [P3 MAIN RAM TONNAGE] REAL NULL,
        [P3 DC TONNAGE] REAL NULL,
        [P3 PUMP 7 PRESSURE TRANSDUCER] REAL NULL,
        [P3 PUMP 8 PRESSURE TRANSDUCER] REAL NULL,
        [P3 PUMP 9 PRESSURE TRANSDUCER] REAL NULL,
        [P3 MAIN RAM B-LINE PRESSURE TRANSDUCER] REAL NULL,
        CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    );
END
ELSE
BEGIN
    IF COL_LENGTH('dbo.MachineDataLog', 'OperatorName') IS NULL
        ALTER TABLE dbo.MachineDataLog ADD OperatorName VARCHAR(200) NULL;

    IF COL_LENGTH('dbo.MachineDataLog', 'Swift') IS NULL
        ALTER TABLE dbo.MachineDataLog ADD Swift VARCHAR(100) NULL;

IF COL_LENGTH('dbo.MachineDataLog', '0.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '0.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [0.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '1.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [1.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '2.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [2.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '3.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [3.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '4.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [4.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '5.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [5.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '6.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [6.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '7.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [7.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '8.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [8.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '9.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [9.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '10.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [10.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '11.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [11.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '12.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [12.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '13.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [13.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '14.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [14.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '15.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [15.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '16.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [16.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '17.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [17.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '18.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [18.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '19.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [19.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '20.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [20.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '21.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [21.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '22.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [22.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '23.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [23.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '24.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [24.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '25.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [25.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '26.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [26.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '27.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [27.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '28.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [28.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '29.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [29.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '30.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [30.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '31.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [31.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '32.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [32.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '33.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [33.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '34.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [34.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.4') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.4] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.5') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.5] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.6') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.6] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '35.7') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [35.7] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '36.0') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [36.0] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '36.1') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [36.1] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '36.2') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [36.2] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', '36.3') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [36.3] BIT NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 MAIN RAM PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 MAIN RAM PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 MAIN RAM POSITION') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 MAIN RAM POSITION] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 DIECUSHION PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 DIECUSHION PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 DIECUSHION POSITION') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 DIECUSHION POSITION] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 DAMPUR PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 DAMPUR PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 OIL LVEL LOW') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 OIL LVEL LOW] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 OIL TEMP HIGH') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 OIL TEMP HIGH] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 CYCLE TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 CYCLE TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 DWELL TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 DWELL TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 PRV.CYCLE TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 PRV.CYCLE TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 SHIFT COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 SHIFT COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 CUMM COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 CUMM COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 MACHINE LIFE COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 MACHINE LIFE COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 MAIN RAM TONNAGE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 MAIN RAM TONNAGE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 DC TONNAGE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 DC TONNAGE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 PUMP 1 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 PUMP 1 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 PUMP 2 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 PUMP 2 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 PUMP 3 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 PUMP 3 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P1 MAIN RAM B-LINE PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P1 MAIN RAM B-LINE PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 MAIN RAM PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 MAIN RAM PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 MAIN RAM POSITION') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 MAIN RAM POSITION] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 DIECUSHION PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 DIECUSHION PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 DIECUSHION POSITION') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 DIECUSHION POSITION] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 DAMPUR PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 DAMPUR PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 OIL LVEL LOW') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 OIL LVEL LOW] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 OIL TEMP HIGH') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 OIL TEMP HIGH] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 CYCLE TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 CYCLE TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 DWELL TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 DWELL TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 PRV.CYCLE TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 PRV.CYCLE TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 SHIFT COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 SHIFT COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 CUMM COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 CUMM COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 MACHINE LIFE COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 MACHINE LIFE COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 MAIN RAM TONNAGE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 MAIN RAM TONNAGE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 DC TONNAGE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 DC TONNAGE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 PUMP 4 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 PUMP 4 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 PUMP 5 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 PUMP 5 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 PUMP 6 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 PUMP 6 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P2 MAIN RAM B-LINE PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P2 MAIN RAM B-LINE PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 MAIN RAM PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 MAIN RAM PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 MAIN RAM POSITION') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 MAIN RAM POSITION] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 DIECUSHION PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 DIECUSHION PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 DIECUSHION POSITION') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 DIECUSHION POSITION] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 DAMPUR PRESSURE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 DAMPUR PRESSURE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 OIL LVEL LOW') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 OIL LVEL LOW] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 OIL TEMP HIGH') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 OIL TEMP HIGH] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 CYCLE TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 CYCLE TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 DWELL TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 DWELL TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 PRV.CYCLE TIME') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 PRV.CYCLE TIME] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 SHIFT COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 SHIFT COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 CUMM COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 CUMM COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 MACHINE LIFE COUNT') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 MACHINE LIFE COUNT] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 MAIN RAM TONNAGE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 MAIN RAM TONNAGE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 DC TONNAGE') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 DC TONNAGE] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 PUMP 7 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 PUMP 7 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 PUMP 8 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 PUMP 8 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 PUMP 9 PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 PUMP 9 PRESSURE TRANSDUCER] REAL NULL;
IF COL_LENGTH('dbo.MachineDataLog', 'P3 MAIN RAM B-LINE PRESSURE TRANSDUCER') IS NULL
    ALTER TABLE dbo.MachineDataLog ADD [P3 MAIN RAM B-LINE PRESSURE TRANSDUCER] REAL NULL;
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_MachineDataLog_Machine_Timestamp' AND object_id = OBJECT_ID('dbo.MachineDataLog'))
BEGIN
    CREATE INDEX IX_MachineDataLog_Machine_Timestamp ON dbo.MachineDataLog(MachineNumber, [Timestamp] DESC);
END
