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
}

syslang = locale.getlocale()
lang = syslang[0]
if lang.find( '_' ) != -1:
    lang = lang[ 0 : lang.find( '_' ) ]
lang = lang.lower()

def printl( msg, args={} ):
    msgArgs = ''
    if lang in messages.get( msg, {} ):
        msgArgs = f'{messages.get( msg, {} ).get( lang ) }'
    else:
        msgArgs = f'{messages.get( msg, {} ).get( "english" ) }'

    if len(args) > 0:
        for key, value in args.items():
            msgArgs = msgArgs.replace( f'${key}$', value )

    print(f'{msgArgs}\n')

#========================================================================
#======================== Rules logic
#========================================================================


def ripent( entdata = [] ):
    # Here lazyripent's rules will be implemented.
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

                entitydata = ripent( entdata = json.load( jsonfile ) )
                newdata = ''

                for entblock in entitydata:
                    newdata += '{\n'
                    for key, value in entblock.items():
                        newdata += f'"{key}" "{value}"\n'
                    newdata += '}\n'

                printl('writting_map', { 'map': map.replace( '.json', '.bsp' ) } )

                bsp_read( map.replace( '.json', '.bsp' ), writedata=newdata )

            os.remove( map )

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
