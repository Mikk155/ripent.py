import os
import json
import locale

from MikkUtils import Ripent, wildcard, format, jsonc

messages = {
    "EnterExit":
    {
        "english": "Press Enter to exit...",
        "spanish": "Presiona Enter para salir...",
    },
    "EnterContinue":
    {
        "english": "Press Enter to continue",
        "spanish": "Presiona Enter para continuar",
    },
    "exit":
    {
        "english": "{} Exit.",
        "spanish": "{} Salir.",
    },
    "export":
    {
        "english": "{} Export entity data",
        "spanish": "{} Exportar datos de entidades",
    },
    "rules":
    {
        "english": "{} Apply logic rules to entity data json",
        "spanish": "{} Aplicar reglas logicas a la informacion de entidades json",
    },
    "rules_path":
    {
        "english": "Locate rules.json in\n{}",
        "spanish": "Pon rules.json en\n{}",
    },
    "import":
    {
        "english": "{} Import entity data",
        "spanish": "{} Importar datos de entidades",
    },
    "export_folder":
    {
        "english": "Locate all the map files that you want to export/import in\n{}",
        "spanish": "Pon todos los archivos de mapas que quieres exportar/importar en\n{}",
    },
    "exporting_map":
    {
        "english": "Exporting {}",
        "spanish": "Exportando {}",
    },
    "importing_map":
    {
        "english": "Writting to {}",
        "spanish": "Escribiendo en {}",
    },
    "delete_jsons":
    {
        "english": "{} Delete json files of entity data",
        "spanish": "{} Elimina los archivos json de informacion de entidades",
    },
    "deleting_json":
    {
        "english": "Deleted {}",
        "spanish": "Eliminado {}",
    },
}

supported = ( '.bsp' )
#supported = ( '.bsp', '.rmf', '.map', '.jmf' )

syslang = locale.getlocale()

lang = syslang[0]

if lang.find( '_' ) != -1:
    lang = lang[ 0 : lang.find( '_' ) ]

lang = lang.lower()

def printl(msg, args={}):
    print( format( messages.get( msg, {} ).get( ( lang if lang in messages.get( msg, {} ) else "english" ) ), args ) + '\n' )

def waitl( msg ):
    printl( msg )
    input("")

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def get_files( path ):
    files = []
    for file in os.listdir( path ):
        if file.endswith( supported ):
            files.append( file )

    return files

def is_matched( entblock = {}, rules = {}, i = 0, mapname='' ):

    selectors = 0   # Rule selectors wants
    passed = 0      # Entity matches rules selectors

    if 'match' in rules:
        for k, v in rules.get( 'match', {} ).items():
            selectors+=1
            if k in entblock and wildcard( entblock.get( k, '' ), v ):
                passed +=1
    if 'not_match' in rules:
        for k, v in rules.get( 'not_match', {} ).items():
            selectors+=1
            if not k in entblock and not wildcard( entblock.get( k, '' ), v ):
                passed +=1
    if 'have' in rules:
        for k in rules.get( 'have', [] ):
            selectors+=1
            if k in entblock:
                passed +=1
    if 'not_have' in rules:
        for k in rules.get( 'not_have', [] ):
            selectors+=1
            if not k in entblock:
                passed +=1

    if 'maps' in rules and len( rules.get( 'maps', [] ) ) > 0:
        selectors+=1
        map_name = mapname[ : mapname.rfind( '.json' ) ]
        if map_name.find( '\\' ) != -1:
            map_name = map_name[ map_name.rfind( '\\' ) +1 : ]
        if map_name.find( '/' ) != -1:
            map_name = map_name[ map_name.rfind( '/' ) +1 : ]
        if map_name in rules.get( 'maps', [] ):
            passed +=1
        else:
            for map in rules.get( 'maps', [] ):
                if wildcard( map_name, map ):
                    passed +=1
                    break

    if selectors > 0 and passed == selectors:
        print(f'applying_rule', { "index": str(i) } )
        return True
    return False

#========================================================================
#======================== main
#========================================================================

abs = f"{os.path.abspath( '' )}\\"

def main():
    clear()
    printl('exit',[ ' [ E ] -'])
    printl('export',[ ' [ 1 ] -'])
    printl('import',[ ' [ 2 ] -'])
    printl('rules',[ ' [ 3 ] -'])
    printl('delete_jsons',[ ' [ 4 ] -'])

    command = input().upper()

    clear()

    if command == 'E':
        exit(0)
    elif command == '1':
        printl('exit',[ ' [ E ] -'])
        printl('export_folder',[ f'"{abs}maps\\"'])
        printl('EnterContinue')
        if input().upper() == 'E':
            exit(0)
        clear()
        maps = get_files( f'{abs}maps\\' )
        for map in maps:
            if map.endswith( supported ):
                mapfile = Ripent( f'{abs}\\maps\\{map}' )
                mapfile.export( True )
                printl('exporting_map', [ map ] )
        waitl( 'EnterContinue' )
    elif command == '2':
        printl('exit',[ ' [ E ] -'])
        printl('export_folder',[ f'"{abs}maps\\"'])
        printl('EnterContinue')
        if input().upper() == 'E':
            exit(0)
        clear()
        maps = get_files( f'{abs}maps\\' )
        for map in maps:
            if map.endswith( '.json' ) and map != 'rules.json':

                r = f'{abs}\\maps\\{map}'
                if os.path.exists( r.replace( '.json', '.bsp' ) ):
                    r = map.replace( '.json', '.bsp' )
                elif os.path.exists( r.replace( '.json', '.map' ) ):
                    r = map.replace( '.json', '.map' )
                elif os.path.exists( r.replace( '.json', '.rmf' ) ):
                    r = map.replace( '.json', '.rmf' )
                elif os.path.exists( r.replace( '.json', '.jmf' ) ):
                    r = map.replace( '.json', '.jmf' )

                entity_data = json.load( open( f'{abs}\\maps\\{map}', 'r' ) )
                mapfile = Ripent( f'{abs}\\maps\\{r}' )
                mapfile.import_( entity_data )
                printl('importing_map', [ map ] )
        waitl( 'EnterContinue' )
    elif command == '3':
        printl('exit',[ ' [ E ] -'])
        printl('rules_path',[ f'"{abs}maps\\rules.json"'])
        printl('EnterContinue')
        if input().upper() == 'E':
            exit(0)
        clear()
        maps = get_files( f'{abs}maps\\' )
        rules_list = jsonc( f'{abs}\\maps\\rules.json' )

        for map in maps:
            if map.endswith( '.json' ) and map != 'rules.json':

                r = f'{abs}\\maps\\{map}'
                if os.path.exists( r.replace( '.json', '.bsp' ) ):
                    r = map.replace( '.json', '.bsp' )
                elif os.path.exists( r.replace( '.json', '.map' ) ):
                    r = map.replace( '.json', '.map' )
                elif os.path.exists( r.replace( '.json', '.rmf' ) ):
                    r = map.replace( '.json', '.rmf' )
                elif os.path.exists( r.replace( '.json', '.jmf' ) ):
                    r = map.replace( '.json', '.jmf' )

                entdata = json.load( open( f'{abs}\\maps\\{map}', 'r' ) )
                mapfile = Ripent( f'{abs}\\maps\\{r}' )
                printl('importing_map', [ map ] )
                mapname=map.replace( '.json', '' )

                NewEntData = []

                for entblock in entdata:

                    SaveEntity = True

                    for i, rules in enumerate(rules_list):

                        # matched all selectors, aplying actions
                        if is_matched( entblock=entblock, rules=rules, i=i, mapname=mapname ):

                            OldEntBlock = entblock.copy() # Used for value-copying

                            if 'delete' in rules and rules.get( 'delete', False ):
                                SaveEntity = False
                                continue

                            if 'new_entity' in rules:
                                for e in rules.get( 'new_entity', [] ):
                                    if len(e) > 0:
                                        for k, v in e.items():
                                            if v.startswith( '$' ):
                                                e[ k ] = OldEntBlock.get( v[1:], '' )
                                        NewEntData.append(e)

                            if 'replace' in rules:
                                for k, v in rules.get( 'replace', {} ).items():
                                    entblock[ k ] = OldEntBlock.get( v[1:], '' ) if v.startswith( '$' ) else v

                            if 'rename' in rules:
                                for k, v in rules.get( 'rename', {} ).items():
                                    entblock.pop( k, '' )
                                    entblock[ v ] = OldEntBlock.get( k, '' )

                            if 'add' in rules:
                                for k, v in rules.get( 'add', {} ).items():
                                    entblock[ k ] = OldEntBlock.get( v[1:], '' ) if v.startswith( '$' ) else v

                            if 'remove' in rules:
                                for k in rules.get( 'remove', [] ):
                                    entblock.pop( k, '' )

                            if len(entblock) == 0: # Somehow a empty entity ended here
                                SaveEntity = False
                                break

                    if SaveEntity:
                        NewEntData.append(entblock)

                mapfile.import_( NewEntData )
                mapfile.export( True )

        waitl( 'EnterContinue' )
    elif command == '4':
        printl('exit',[ ' [ E ] -'])
        printl('EnterContinue')
        if input().upper() == 'E':
            exit(0)
        clear()
        maps = get_files( f'{abs}maps\\' )
        for map in maps:
            if map.endswith( supported ):
                ptz = f'{abs}\\maps\\{map[ : map.rfind( "." ) ]}.json'
                if os.path.exists( ptz ):
                    printl('deleting_json', [ ptz ] )
                    os.remove( ptz )
        waitl( 'EnterContinue' )
    main()

main()
