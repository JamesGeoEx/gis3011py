#import Psycopg2 for interacting with PostgreSQL/PostGIS
import psycopg2
import psycopg2.extras
import sys
import pandas as pd

def connectToPostGIS(credentials):
    try:
        conn_string = f"postgresql://{str(credentials.get('user'))}:{str(credentials.get('password'))}@{str(credentials.get('host'))}:{str(credentials.get('port'))}/{str(credentials.get('database'))}"
        
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
    except psycopg2.OperationalError as exc:
        print(exc.message)
    return conn, cursor

# We could just write all the column names and types as a list, but at times we need the name and type, and at other times
# we only need the name. This allows us to write a single dictionary for the table and prepare it into two correctly
# formatted lists to use throughout the script. First, we convert the dictionary to a list, then we format the list to 
# a string in the correct format
def prepareTableColumns(table_column_details):
    table_columns_list = []
    names_list = []
    primary_key_choice = 'not_set'
    
    for key, value in table_column_details.items():
        if value.endswith('primary key'):
            if primary_key_choice == 'not_set':
                print("You have elected to use a primary key. This means you will not be able to append a list without first setting the primary key value to start with the next avaliable integer.")
                while True:
                    confirm_primary_key = input("Would you like to continue with using a primary key? (y/n)")
                    if confirm_primary_key not in ('n', 'y'):
                        print("I didn't understand the command. Please use 'y' or 'n'")
                        continue
                    elif confirm_primary_key =='y':
                        primary_key_choice = 'yes'
                        break
                    elif confirm_primary_key =='n': 
                        primary_key_choice = 'no'
                        table_columns_list.append("Not prepared")
                        names_list.append("Not prepared")
                        print("Okay, you'll need to go back to the list of table column information and delete the words 'primary key', then run the cell again.")
                        print("No table columns have been prepared. They must be prepared before continuing.")
                        break  
        if primary_key_choice == 'not_set' or primary_key_choice == 'yes':           
            # Tell python we only want the key and the value ('key' 'value'), not a key/value pair 
            # seperated by a comma or colon ('key' : 'value'), however, it will still print with ''
            one_column = f"{key} {value}"
            table_columns_list.append(one_column)    
            
            #And the list of just names seperated by a comma
            one_column_name = f"{key}"
            names_list.append(one_column_name)
              
    # https://www.geeksforgeeks.org/python-ways-to-print-list-without-quotes/
    # Also, Postgres wants the tuple of columns in () not a list with [],  
    # so we need to format the string a bit more
    # example: (key value, key value, key value)
    table_columns=str(f"({', '.join(table_columns_list)})")            
    column_names=str(f"({', '.join(names_list)})")
    column_list = list(table_column_details.keys())
    
    print("Table Names List Formatted String: " + column_names)
    print("Table Columns Formatted String: " + table_columns)
    print("Tables Columns as Formatted List: " + str(column_list))
            
    return column_names, table_columns, column_list
    
def createOrUpdateNewTable(credentials, table_name, table_columns, truncate_confirm='n'):
    # Check if the table exists already
    # If the table does already exist, see how many records are present
    if (tableExists(credentials, table_name)) is True:
        print("Table already exists")
        
        row_count = countTableRows(credentials, table_name)    
        if row_count > 0:
            print("There are already " + str(row_count) + " records in the table.  You will need to truncate the table's records if you set the OID to the primary key.")   
            while True:
                truncate_confirm = input("Would you like to truncate the table? (y/n)")
                if truncate_confirm not in ('n', 'y'):
                    print("I didn't understand the command. Please use 'y' or 'n'")
                    continue
                elif truncate_confirm == 'y':
                    #Connect to the database
                    conn, cursor = connectToPostGIS(credentials)

                    #Truncate all the rows in the table so that you're not appending to existing data
                    queries = [f"TRUNCATE {table_name};", f"DELETE FROM {table_name};"]
                    for query in queries:
                        try:
                            cursor.execute(query)
                            # committing changes
                            conn.commit()
                            print("Executed: ", query)
                        except psycopg2.OperationalError as exc:
                            print(exc.message)
                    #Count the rows again to make sure it's now empty
                    row_count = countTableRows(credentials, table_name)
                    print("New record count: " + str(row_count))
                    break
                elif truncate_confirm == 'n':
                    print("Okay, no records were deleted")
                    break
        else:
            print("Table has no records (is empty)")
    else:
        conn, cursor = connectToPostGIS(credentials)
        cursor.execute(f"create table {table_name}{table_columns}")
        # committing changes
        conn.commit()
        # closing connection
        conn.close()
        print(f"Created table: {table_name} in {str(credentials.get('database'))}")

def tableExists(credentials, table_name):
    exists = False
    conn, cursor = connectToPostGIS(credentials)
    try:
        cursor.execute(f"SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = '{table_name}');")
        exists = cursor.fetchone()[0]
        conn.close()
    except psycopg2.OperationalError as exc:
        print(exc.message)
    return exists

def countTableRows(credentials, table_name):
    conn, cursor = connectToPostGIS(credentials)
    try:
        cursor.execute(f"SELECT COUNT (*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        conn.close()
    except psycopg2.OperationalError as exc:
        print(exc.message)
    return row_count

def writeRecordsToTable(credentials, table_name, column_names, records, print_result=True):
    conn, cursor = connectToPostGIS(credentials)
    try:
        #Insert the array of records into the database
        psycopg2.extras.execute_values(cursor, f"INSERT INTO {table_name} {column_names} VALUES %s", records)
        #Print the result
        if print_result is True:
            cursor.execute(f"SELECT * FROM {table_name};")
            # fetching rows
            for i in cursor.fetchall():
                print(i)
        conn.commit()
        conn.close()
        
        if print_result is True:
            row_count = countTableRows(credentials, table_name) 
            print(f"Added {str(row_count)} rows to {table_name}")
    except psycopg2.OperationalError as exc:
        print(exc.message)

def csvToPostGIS(credentials, table_name, csv):
    conn, cursor = connectToPostGIS(credentials)
    try:
        cursor.execute(f"COPY {table_name} FROM '{csv}' DELIMITER ',' CSV HEADER;")
        conn.commit()
        conn.close()
    except psycopg2.OperationalError as exc:
        print(exc.message)
        
        
def readPostGISTableAsDF(credentials, table_name, column_list):
    conn, cursor = connectToPostGIS(credentials)

    try:
        # The cursor.execute returns a list of tuples:
        cursor.execute(f"SELECT * FROM {table_name};")
        tuples_list = cursor.fetchall()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
    
    # Now we need to transform the list into a pandas DataFrame:
    df = pd.DataFrame(data=tuples_list, columns=column_list)
    return df

def writeDFtoPostGISTable(credentials, df, table_name, column_names):
    conn, cursor = connectToPostGIS(credentials)
    
    tuples = [tuple(x) for x in df.to_numpy()]
    print(tuples)

    try:
        psycopg2.extras.execute_values(cursor, f"INSERT INTO {table_name} {column_names} VALUES %s", tuples)
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    
    print("the dataframe is inserted")
    cursor.close()
        
def createNewPostGISFunctions(credentials):
    conn, cursor = connectToPostGIS(credentials)
    
    try:
        cursor.execute('''CREATE OR REPLACE FUNCTION column_exists(ptable text, pcolumn text, pschema text default 'public') 
            RETURNS  boolean 
            LANGUAGE sql stable strict  
        AS $body$
            select exists 
                 ( select null 
                     from information_schema.columns 
                     where table_name=ptable 
                       and column_name=pcolumn 
                       and table_schema=pschema
                 ); 
        $body$;

        CREATE OR REPLACE FUNCTION rename_column_if_exists(ptable TEXT, pcolumn TEXT, new_name TEXT)
            RETURNS VOID AS $BODY$
        BEGIN
            IF column_exists(ptable, pcolumn) THEN
                EXECUTE FORMAT('ALTER TABLE %I RENAME COLUMN %I TO %I;',
                    ptable, pcolumn, new_name);
            END IF;
        END$BODY$
        LANGUAGE plpgsql VOLATILE; 
            
        CREATE OR REPLACE FUNCTION rowjsonb_to_geojson(
            rowjsonb JSONB, 
            geometry TEXT DEFAULT 'geom')
        RETURNS TEXT AS 
        $$
        DECLARE 
            json_props jsonb;
            json_geom jsonb;
            json_type jsonb;
        BEGIN
            IF NOT rowjsonb ? geometry THEN
                RAISE EXCEPTION 'geometry column column ''%'' is missing', geometry;
            END IF;
            json_geom := ST_AsGeoJSON((rowjsonb ->> geometry)::geometry)::jsonb;
            json_geom := jsonb_build_object('geom', json_geom);
            json_props := jsonb_build_object('properties', rowjsonb - geometry);
            json_type := jsonb_build_object('type', 'Feature');
            return (json_type || json_geom || json_props)::text;
        END; 
        $$ 
        LANGUAGE 'plpgsql' IMMUTABLE STRICT;''')
        conn.commit()
        conn.close()
        print(f"Additional functions added to {str(credentials.get('database'))}")
        
    except psycopg2.OperationalError as exc:
        print(exc.message)