BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "amqp"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml'] #'pickle'
CELERY_IMPORTS = ("dam.mprocessor.processor", 
                  "dam.mprocessor.servers.generic_cmd",
                  "dam.mprocessor.servers.xmp_embedder",
                  "dam.mprocessor.servers.xmp_extractor",)
