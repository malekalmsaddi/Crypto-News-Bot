import sentry_sdk

sentry_sdk.init(
    dsn="https://b5b64b8d7d2f02d33d58b3efe129d757@o4509078491955200.ingest.us.sentry.io/4509078495428608",
    # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
    traces_sample_rate=1.0,
)