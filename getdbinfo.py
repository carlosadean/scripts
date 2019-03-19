#!/usr/bin/env python
#from tools.portaldb import PortalDB
from tools.admindb import AdminDB
from tools.gavo.dao import CatalogDB
import datetime
import lib.log
import logging
import os
import re


def DiffList(l1, l2, rev=False):
    if rev:
        return list(set(l2) - set(l1))
    else:
        return list(set(l1) - set(l2))

def IntersList(l1, l2):
    return list(set(l2) & set(l1))

# remover as tabelas cujo nome casa com a regex - catalogo primario
def remove_tables_product_and_hpix(tableslist, quiet=False):
    newTablesList = []
    # https://regex101.com/r/YbqVxL/2
    # regex = '(^(SV|Y[1-5])[A|N|T|P][0-9]{1,2}_COADD)'
    # regex = '^.+_([0-9]{2,8}|hpix|keys|g|r|i|z|y)'
    # regex = '^.+_([0-9]{2,8}|hpix|keys|g|r|i|z|y|nest|ring|tiles|test|all[0-9]{1,})'

    # https://regex101.com/r/YbqVxL/5
    regex = '^.+_([0-9]{3,8}|hpix|keys|_g|_r|_i|_z|_y|tmp|nest|ring|tiles|test|all[0-9]{1,})'

    c = 1
    t = 1
    for table in tableslist:
        if re.match(regex, table):
            t += 1
            #print('%s REMOVED: %s' % (str(t),table))
            newTablesList.append(table)
        else:
            if quiet:
            #print('%s %s' % (str(c), table))
                c += 1
            else:
                print('%s %s' % (str(c),table))
                c += 1
    
    return newTablesList


# global variables
portal_root = os.environ['PORTAL_ROOT']
logdir = os.path.join(portal_root, 'logs')
logfile_sufix = '.log' #datetime.datetime.now().strftime('%Y%m%d-%H%M.log')
logger = logging.getLogger('[DBINFO]')

# logging information

# logfile_path = os.path.join(logdir, logfile_name)
# if not os.path.exists(logdir):
#     os.makedirs(logdir)
# logger = logging.getLogger('[catalogdb]')
# handler = logging.FileHandler(logfile_path)
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s:[%(levelname)s]:%(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# catalogdb log file
logfile_name = 'prod-get_database_info-' + str(logfile_sufix)
#logfile_path = os.path.join(logdir, logfile_name)
logfile_path = os.path.join('/home/carlosadean/portal/logs/', logfile_name)
logging.basicConfig(format="[%(levelname)s] %(asctime)s: %(message)s",\
                datefmt="%Y-%m-%d %H:%M:%S",  level=logging.INFO,\
                filename=logfile_path)

# catalogDB
# logger = lib.log.get_logger("TABLES CATALOGDB")
#logger.info('identifying catalog database tables')

ignored_schemas ="'pg_catalog', 'information_schema', 'dc','tno'"

sql = """
    SELECT
        nspname || '.' || relname AS "relation" 
    FROM
        pg_class c 
        LEFT JOIN
            pg_namespace n 
            ON (n.oid = c.relnamespace) 
    WHERE
        nspname NOT IN 
        (
            % s
        )
        AND c.relkind <> 'i' 
        AND nspname !~ '^pg_toast';
""" % ignored_schemas

# [1] todas as tabelas existentes somente no catalogdb
catalogdb = CatalogDB()
res_catalogdb = catalogdb.executeIndependentQuery(sql)
res_catalogdb = map(' '.join, res_catalogdb.fetchall())
res_catalogdb = sorted(res_catalogdb)
n_catalogdb_tables = len(res_catalogdb)
msg = 'THERE ARE ' + str(n_catalogdb_tables) + ' TABLES IN THE CATALOGDB'
logger.info(msg)
print(msg)

# adminDB
logger = lib.log.get_logger("TABLES ADMINDB")
#logger.info('identifying registered tables in the admindb')

# lista de produtos-tabela do portal
sql = """
    SELECT
        tables.schema_name || '.' || tables.table_name AS "TABLE" 
    FROM
        products 
        INNER JOIN
            tables 
            ON products.table_id = tables.table_id;
"""

# [2] todas as tabelas existentes somente no admindb
admindb = AdminDB()
res_products = admindb.executeIndependentQuery(sql)
res_products = map(' '.join, res_products.fetchall())
res_products = sorted(res_products)
n_admindb_tables = len(res_products)
msg = 'THERE ARE ' + str(n_admindb_tables) + ' TABLES REGISTERED AS A PRODUCT IN THE ADMINDB'
logger.info(msg)
print(msg)


# job_runs.job_id,
# processes.process_id,
# processes.status_id
# produtos/tabelas que estao associadas a processos salvos
sql = """
    SELECT
        tables.schema_name || '.' || tables.table_name AS "TABLE"
    FROM
        products 
        INNER JOIN
            tables 
            ON products.table_id = tables.table_id 
        INNER JOIN
            job_runs 
            ON job_runs.job_id = products.job_id 
        INNER JOIN
            processes 
            ON job_runs.process_id = processes.process_id 
        INNER JOIN
            process_status 
            ON process_status.process_status_id = processes.status_id
        WHERE processes.status_id = 1
"""
res_products_in_saved_processes = admindb.executeIndependentQuery(sql)
res_products_in_saved_processes = map(' '.join, res_products_in_saved_processes.fetchall())
res_products_in_saved_processes = sorted(res_products_in_saved_processes)
n_products_in_saved_processes = len(res_products_in_saved_processes)
msg = 'THERE ARE ' + str(n_products_in_saved_processes) + ' TABLES REGISTERED AND ASSOCIATED WITH A SUCCESS PROCESS [SAVED]'
logger.info(msg)
print(msg)


# job_runs.job_id,
# processes.process_id,
# processes.status_id
# listar tabelas cujos produtos estao associados a processos salvos e cujo status e 'failure'
sql = """
    SELECT
        tables.schema_name || '.' || tables.table_name AS "table"
    FROM
        products 
        INNER JOIN
            tables 
            ON products.table_id = tables.table_id 
        INNER JOIN
            job_runs 
            ON job_runs.job_id = products.job_id 
        INNER JOIN
            processes 
            ON job_runs.process_id = processes.process_id 
        INNER JOIN
            process_status 
            ON process_status.process_status_id = processes.status_id 
        INNER JOIN
            saved_processes 
            ON saved_processes.process_id = processes.process_id 
    WHERE
        processes.status_id = 3 ;
"""
res_products_in_saved_failed_processes = admindb.executeIndependentQuery(sql)
res_products_in_saved_failed_processes = map(' '.join, res_products_in_saved_failed_processes.fetchall())
res_products_in_saved_failed_processes = sorted(res_products_in_saved_failed_processes)
n_products_in_saved_failed_processes = len(res_products_in_saved_failed_processes)
msg = 'THERE ARE ' + str(n_products_in_saved_failed_processes) + ' TABLES REGISTERED AND ASSOCIATED WITH A FAILED PROCESS [SAVED]'
logger.info(msg)
print(msg)

# calculating the difference between admindb and catalogdb
# logger = lib.log.get_logger("DIFFERENCE BETWEEN TABLES")
#logger.info('identifying difference between the databases')

# [3] todas as tabelas comuns ao catalogdb e ao admindb
intersection_catalogdb_to_admindb = sorted(IntersList(res_catalogdb, res_products))
msg = 'THERE ARE ' + str(len(intersection_catalogdb_to_admindb)) + ' TABLES IDENTIFIED IN BOTH DATABASES CATALODB AND ADMINDB'
logger.info(msg)
print(msg)

# [4] tables existing in the catalodb but not registered in the admindb
difference_catalogdb_to_admindb = sorted(DiffList(res_catalogdb, res_products, rev=False))
msg = 'THERE ARE ' + str(len(difference_catalogdb_to_admindb)) + ' TABLES IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB'
logger.info(msg)
print(msg)
# TODO: store the tables in a txt file: DONE

# [4.1] similar to [4] but it is applying a filter to remove all 'primary tables' according to the regex
# tables existing in the catalodb but not registered in the admindb
difference_catalogdb_to_admindb_filtered = remove_tables_product_and_hpix(difference_catalogdb_to_admindb,quiet=True)
difference_unregistered_tables_filtered = sorted(DiffList(difference_catalogdb_to_admindb, difference_catalogdb_to_admindb_filtered, rev=False))
msg = 'THERE ARE ' + str(len(difference_unregistered_tables_filtered)) + ' TABLES IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB (FILTERED BY REGEX)'
logger.info(msg)
print(msg)

# [4.2] similar to [4.1] but instead of shows the filtered list it shows the intersection
# tables existing in the catalodb but not registered in the admindb
intersection_unregistered_tables_filtered = sorted(IntersList(difference_catalogdb_to_admindb, difference_catalogdb_to_admindb_filtered))
msg = 'THERE ARE ' + str(len(intersection_unregistered_tables_filtered)) + ' IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB (FILTERED BY REGEX)[INTERSECTION]'
logger.info(msg)
print(msg)

# [5] tables registered in the admindb but not existing in the catalogdb
difference_admindb_to_catalogdb = sorted(DiffList(res_catalogdb, res_products, rev=True))
msg = 'THERE ARE ' + str(len(difference_admindb_to_catalogdb)) + ' TABLES IDENTIFIED IN THE ADMINDB NOT EXISTING IN THE CATALOGDB'
logger.info(msg)
print(msg)

# [6] tables existing in the catalodb, registered in the admindb that its process is saved and the process status is success
difference_admindb_to_catalogdb_saved = sorted(IntersList(res_catalogdb, res_products_in_saved_processes))
msg = 'THERE ARE ' + str(len(difference_admindb_to_catalogdb_saved)) + ' TABLES IN THE CATALOGDB REGISTERED WITH A SUCCESSFUL PROCESS [SAVED]'
logger.info(msg)
print(msg)

# [7] tables existing in the catalodb, registered in the admindb that its process is saved and the process status is failure
difference_admindb_to_catalogdb_saved_failed = sorted(IntersList(res_catalogdb, res_products_in_saved_failed_processes))
msg = 'THERE ARE ' + str(len(difference_admindb_to_catalogdb_saved_failed)) + ' TABLES IN THE CATALOGDB REGISTERED WITH A FAILED PROCESS [SAVED]'
logger.info(msg)
print(msg)

# tabelas existentes no catalogdb
logger.info('################# LIST OF ALL TABLES IN THE CATALOGDB ################')
numb = 1
for dtable in res_catalogdb:
    logger.info('catalogdb: (' + str(numb) + ' of ' + str(len(res_catalogdb)) +') ' + dtable)
    numb += 1
logger.info('*********************** END ALL TABLES IN THE CATALOGDB **************************')

# tabelas existentes no admindb
logger.info('################# TABLES IDENTIFIED IN THE ADMINDB NOT EXISTING IN THE CATALOGDB ################')
numb = 1
for dtable in difference_admindb_to_catalogdb:
    logger.info('admindb: (' + str(numb) + ' of ' + str(len(difference_admindb_to_catalogdb)) +') ' + dtable)
    numb += 1
logger.info('******************* END TABLES IDENTIFIED IN THE ADMINDB NOT EXISTING IN THE CATALOGDB ***********************')

# tabelas existentes no admindb com processos salvos mesmo com status failure
logger.info('################# TABLES REGISTERED AND ASSOCIATED WITH A SUCCESS PROCESS [SAVED] ################')
numb = 1
for dtable in difference_admindb_to_catalogdb_saved:
    logger.info('admindb success saved: (' + str(numb) + ' of ' + str(len(difference_admindb_to_catalogdb_saved)) +') ' + dtable)
    numb += 1
logger.info('****************** END TABLES REGISTERED AND ASSOCIATED WITH A SUCCESS PROCESS [SAVED] ************************')

# tabelas existentes no admindb com processos salvos mesmo com status failure
logger.info('################# TABLES REGISTERED AND ASSOCIATED WITH A FAILED PROCESS [SAVED] ################')
numb = 1
for dtable in difference_admindb_to_catalogdb_saved_failed:
    logger.info('admindb failed saved: (' + str(numb) + ' of ' + str(len(difference_admindb_to_catalogdb_saved_failed)) +') ' + dtable)
    numb += 1
logger.info('********************* END TABLES REGISTERED AND ASSOCIATED WITH A FAILED PROCESS [SAVED] ********************')

# tabelas existentes no admindb com processos salvos mesmo com status failure
logger.info('################# TABLES IDENTIFIED IN BOTH DATABASES CATALODB AND ADMINDB ################')
numb = 1
for dtable in intersection_catalogdb_to_admindb:
    logger.info('tables in both: (' + str(numb) + ' of ' + str(len(intersection_catalogdb_to_admindb)) +') ' + dtable)
    numb += 1
logger.info('******************** END TABLES IDENTIFIED IN BOTH DATABASES CATALODB AND ADMINDB *******************')

# tabelas existentes no catalogdb e que nao aparecem registradas no admindb
# e' preciso identificar quem e' catalogo primario e quem nao e
logger.info('################# TABLES IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB ################')
numb = 1
for dtable in difference_catalogdb_to_admindb:
    logger.info('catalogdb unregistered in admindb: (' + str(numb) + ' of ' + str(len(difference_catalogdb_to_admindb)) +') ' + dtable)
    numb += 1
logger.info('******************** END IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB ********************')

# lista de tabelas filtradas da lista acima e que supostamentesimilar a anterior, porem filtradas as tabetabelas existentes no catalogdb e que nao aparecem registradas no admindb
# e' preciso identificar quem e' catalogo primario e quem nao e
logger.info('################# TABLES IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB (FILTERED BY REGEX) ################')
numb = 1
for dtable in difference_unregistered_tables_filtered:
    logger.info('catalogdb unregistered in admindb (filtered): (' + str(numb) + ' of ' + str(len(difference_unregistered_tables_filtered)) +') ' + dtable)
    numb += 1
logger.info('******************** END IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB (FILTERED BY REGEX) ********************')

# lista de tabelas filtradas da lista acima e que supostamentesimilar a anterior, porem filtradas as tabetabelas existentes no catalogdb e que nao aparecem registradas no admindb
# e' preciso identificar quem e' catalogo primario e quem nao e
logger.info('################# TABLES IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB (FILTERED BY REGEX)[INTERSECTION] ################')
numb = 1
for dtable in intersection_unregistered_tables_filtered:
    logger.info('catalogdb unregistered in admindb (filtered): (' + str(numb) + ' of ' + str(len(intersection_unregistered_tables_filtered)) +') ' + dtable)
    numb += 1
    print(dtable)
logger.info('******************** END IDENTIFIED IN THE CATALODB UNREGISTERED IN THE ADMINDB (FILTERED BY REGEX)[INTERSECTION] ********************')

#t = remove_tables_product_and_hpix(difference_catalogdb_to_admindb)
