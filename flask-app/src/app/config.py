class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'your_secret_key'
    DATABASE_URI = 'sqlite:///your_database.db'

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev_database.db'

class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = 'sqlite:///test_database.db'

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user:password@localhost/prod_database'  # Update with your production database URI

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}