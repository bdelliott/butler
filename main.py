from butler import sync
import config

if __name__=='__main__':
    config.setup_logging()
    sync.sync_shows()
