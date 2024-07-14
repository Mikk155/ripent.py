import os
import sys
import json
import locale
import platform

#========================================================================
#======================== Message stuff
#========================================================================

messages = {
    "press_input":
    {
        "english": "Press Enter to exit...",
        "spanish": "Presiona Enter para salir...",
    },
    "drag_and_drop_bsp":
    {
        "english": "Drag and drop a BSP file to the script to extract the entity data.",
        "spanish": "Arrastra y suelta un archivo BSP el script para extraer la informacion de entidades.",
    },
    "drag_and_drop_ent":
    {
        "english": "Drag and drop a JSON file to the script to import the entity data.",
        "spanish": "Arrastra y suelta un archivo JSON a el script para importar la informacion de entidades.",
    },
    "sys_export":
    {
        "english": "Write the absolute path to a BSP file to extract the entity data.",
        "spanish": "Escribe la ruta completa hacia un archivo BSP para exportar la informacion de entidades.",
    },
    "sys_import":
    {
        "english": "Write the absolute path to a JSON file to import the entity data.",
        "spanish": "Escribe la ruta completa hacia un archivo JSON para importar la informacion de entidades.",
    },
    "sys_all":
    {
        "english": "$cmd$ \"Absolute/path/to/a/folder\"",
        "spanish": "$cmd$ \"Ruta/completa/hacia/una/carpeta\"",
    },
    "skipping_map":
    {
        "english": "Something went wrong, Skipping map $map$",
        "spanish": "Algo salio mal, Saltando mapa $map$",
    },
    "writting_map":
    {
        "english": "Writting to $map$",
        "spanish": "Escribiendo en $map$",
    },
    "apply_rules":
    {
        "english": "Press R and enter to apply rules.json into the BSP files. Press Enter to not.",
        "spanish": "Presiona R y Enter para aplicar rules.json dentro de los archivos BSP. Presiona Enter para no hacerlo.",
    },
    "applying_rule":
    {
        "english": "Applying rule $index$...",
        "spanish": "Aplicando regla $index$...",
    },
}

syslang = locale.getlocale()
lang = syslang[0]
if lang.find( '_' ) != -1:
    lang = lang[ 0 : lang.find( '_' ) ]
lang = lang.lower()

def cornc(msg, args={}):
    msgArgs = ''
    if lang in messages.get( msg, {} ):
        msgArgs = f'{messages.get( msg, {} ).get( lang ) }'
    else:
        msgArgs = f'{messages.get( msg, {} ).get( "english" ) }'

    if len(args) > 0:
        for key, value in args.items():
            msgArgs = msgArgs.replace( f'${key}$', value )
    return msgArgs

def printl( msg, args={} ):
    print(f'{cornc(msg, args)}\n')

def log( msg, args={} ):
    print(f'{cornc(msg, args)}')

#========================================================================
#======================== Rules logic
#========================================================================

def get_rules():

    js = {}

    with open( os.path.abspath( 'rules.json' ), 'r' ) as file:

        jsdata = ''
        lines = file.readlines()

        for t, line in enumerate( lines ):

            line = line.strip()

            if line and line != '' and not line.startswith( '//' ):
                jsdata = f'{jsdata}\n{line}'

        js = json.loads( jsdata )
        file.close()

    return js

def wildcard( _f, _t ):

    if _f == _t or _f.startswith('*') and _t.endswith(_f[1:]) or _f.endswith('*') and _t.startswith(_f[:len(_f)-1]):
        return True
    return False

def is_matched( entblock = {} ):

    rules_list = get_rules()

    selectors = 0   # Rule selectors wants
    passed = 0      # Entity matches rules selectors

    for i, rules in enumerate(rules_list):

        if 'match' in rules:
            for k, v in rules.get( 'match', {} ).items():
                selectors+=1
                if k in entblock and wildcard( v, entblock.get( k, '' ) ):
                    passed +=1
        if 'not_match' in rules:
            for k, v in rules.get( 'not_match', {} ).items():
                selectors+=1
                if not k in entblock and not wildcard( v, entblock.get( k, '' ) ):
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
    if selectors > 0 and passed == selectors:
        log(f'applying_rule', { "index": str(i) } )
        return True
    return False

def ripent( entdata = [] ):

    NewEntData = []

    for entblock in entdata:

        # matched all selectors, aplying actions
        if is_matched( entblock ):
            # -TODO
            NewEntData.append(entblock)
            continue

        NewEntData.append(entblock)

    return entdata

#========================================================================
#======================== Formatting logic
#========================================================================

def bsp_read( bsp_name, writedata = None ):

    with open( bsp_name, 'r+b' ) as bsp_file:
        bsp_file.read(4) # BSP version.
        read_start = int.from_bytes( bsp_file.read(4), byteorder='little' )
        read_len = int.from_bytes( bsp_file.read(4), byteorder='little' )
        bsp_file.seek( read_start )

        if writedata != None:
            bsp_file.write( writedata.encode() )
            if len( writedata ) < read_len:
                bsp_file.write( b'\x00' * (read_len - len( writedata ) ) )
        else:
            entities_lump = bsp_file.read( read_len )
            return entities_lump.decode('ascii').splitlines()
    return None

def convert( maps=[] ):

    APPLY_RULES = False

    if maps[0].endswith( '.json' ):

        printl('apply_rules')
        ApplyRules = input()

        if ApplyRules.upper() == 'R':
            APPLY_RULES = True

    for map in maps:

        if map.endswith( '.bsp' ):

            entdata = []

            lines = bsp_read( map )

            if lines == None:
                printl('skipping_map', { 'map': map } )
                continue

            entity = {}
            oldline = ''

            for line in lines:

                if line == '{':
                    continue

                line = line.strip()

                if not line.endswith( '"' ):
                    oldline = line
                elif oldline != '' and not line.startswith( '"' ):
                    line = f'{oldline}{line}'

                if line.find( '\\' ) != -1:
                    line = line.replace( '\\', '\\\\' )

                line = line.strip( '"' )

                if not line or line == '':
                    continue

                if line.startswith( '}' ): # startswith due to [NULL]
                    entdata.append( json.dumps( entity ) )
                    entity.clear()
                else:
                    keyvalues = line.split( '" "' )
                    if len( keyvalues ) == 2:
                        entity[ keyvalues[0] ] = keyvalues[1]

            with open( map.replace( '.bsp', '.json' ), 'w' ) as jsonfile:

                printl('writting_map', { 'map': map.replace( '.bsp', '.json' ) } )

                jsonfile.write( '[\n' )
                FirstBlockOf = True
                FirstKeyOf = True

                for entblock in entdata:

                    if FirstBlockOf:
                        FirstBlockOf = False
                    else:
                        jsonfile.write( ',\n' )

                    FirstKeyOf = True

                    jsonfile.write( '\t{\n' )

                    for key, value in json.loads( entblock ).items():

                        if FirstKeyOf:
                            FirstKeyOf = False
                        else:
                            jsonfile.write( ',\n' )

                        jsonfile.write( f'\t\t"{key}": "{value}"' )

                    jsonfile.write( '\n\t}' )

                jsonfile.write( '\n]\n' )
                jsonfile.close()

        elif map.endswith( '.json' ) and os.path.exists( map.replace( '.json', '.bsp' ) ):

            with open( map, 'r' ) as jsonfile:

                entitydata = json.load( jsonfile )

                if APPLY_RULES:
                    entitydata = ripent( entdata = entitydata )

                newdata = ''

                for entblock in entitydata:
                    newdata += '{\n'
                    for key, value in entblock.items():
                        newdata += f'"{key}" "{value}"\n'
                    newdata += '}\n'

                printl('writting_map', { 'map': map.replace( '.json', '.bsp' ) } )

                bsp_read( map.replace( '.json', '.bsp' ), writedata=newdata )

            #os.remove( map )

#========================================================================
#======================== Inputs
#========================================================================
print('')
if len(sys.argv) == 1:
    printl('drag_and_drop_bsp')
    printl('drag_and_drop_ent')
    printl('sys_export')
    printl('sys_import')
    printl('sys_all', { 'cmd':'-import' })
    printl('sys_all', { 'cmd':'-export' })
    printl('press_input')
    sys.argv = input("").split()
if len(sys.argv) >= 1:
    maps=[]
    if sys.argv[0] in [ '-export', '-import' ]:
        folder = os.path.abspath( '' )+'\\'
        if len(sys.argv) > 1 and not sys.argv[1].endswith( '\\' ) and not sys.argv[1].endswith( '/' ):
            folder =f'{sys.argv[1]}\\'
        for file in os.listdir( f'{folder}'):
            if sys.argv[0] == '-export' and file.endswith( ".bsp" ) or sys.argv[0] == '-import' and file.endswith( ".json" ):
                maps.append(file)
    else:
        maps = sys.argv
        if maps[0].endswith( '.py' ):
            maps.pop(0)
    if len(maps) > 0:
        convert( maps=maps )
