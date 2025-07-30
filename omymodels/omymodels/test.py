from omymodels import convert_models, create_models

ddl = """CREATE TABLE [dbo].[users_WorkSchedule](
        [id] [int] IDENTITY(1,1) NOT NULL,
        [RequestDropDate] [smalldatetime] NULL,
        [ShiftClass] [varchar](5) NULL,
        [StartHistory] [datetime2](7) GENERATED ALWAYS AS ROW START NOT NULL,
        [EndHistory] [datetime2](7) GENERATED ALWAYS AS ROW END NOT NULL,
        CONSTRAINT [PK_users_WorkSchedule_id] PRIMARY KEY CLUSTERED
        (
            [id] ASC
        )
        WITH (
            PAD_INDEX = OFF,
            STATISTICS_NORECOMPUTE = OFF,
            IGNORE_DUP_KEY = OFF,
            ALLOW_ROW_LOCKS = ON,
            ALLOW_PAGE_LOCKS = ON
        )  ON [PRIMARY],
        PERIOD FOR SYSTEM_TIME ([StartHistory], [EndHistory])
    )
  """
result = create_models(ddl)
#result = convert_models(models_from, models_type="gino")
print(result['code'])
