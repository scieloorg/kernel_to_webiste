from dsm import configuration
from dsm import ingestion


fs = configuration.get_files_storage()
dbu = configuration.get_db_url()
v3m = configuration.get_pid_manager()
dm = ingestion.DocsManager(fs, dbu, v3m)

pkg_path = '/home/rafael/Working/scielo/scielo-publishing-framework/rt-dsm/tests/fixtures/package.zip'
