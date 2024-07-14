

import os
import sys
import locale
import platform

#========================================================================
#======================== Message stuff
#========================================================================

messages = {
    "press_input":
    {
        "english": "",
        "spanish": "Presiona Enter para salir...",
    },
    "drag_and_drop_bsp":
    {
        "english": "",
        "spanish": "Arrastra y suelta un archivo BSP el script para extraer la informacion de entidades.",
    },
    "drag_and_drop_ent":
    {
        "english": "",
        "spanish": "Arrastra y suelta un archivo JSON a el script para importar la informacion de entidades.",
    },
    "sys_export":
    {
        "english": "",
        "spanish": "Escribe la ruta completa hacia un archivo BSP para exportar la informacion de entidades.",
    },
    "sys_import":
    {
        "english": "",
        "spanish": "Escribe la ruta completa hacia un archivo JSON para importar la informacion de entidades.",
    },
    "sys_all":
    {
        "english": "",
        "spanish": "$cmd$ \"Ruta/completa/hacia/una/carpeta\"",
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
#======================== Use the proper tool
#========================================================================

OS = int(platform.architecture()[0][:2])
ripbits = 'Ripent_x64' if ( OS == 64 ) else 'Ripent'
RIPENT = f'{os.path.abspath( "" )}\\{ripbits}.exe'

#========================================================================
#======================== Formatting logic
#========================================================================

import json
import subprocess

def ripent( entdata = [] ):
    s=''

def convert( maps=[] ):

    for map in maps:

        if map.endswith( '.bsp' ):

            print( f'{RIPENT}')
            print( f'{map}')
            subprocess.call( [ RIPENT, "-export", map ], stdout = open( os.devnull, "wb" ) )

            entdata = []

            with open( map.replace( '.bsp', '.ent' ), 'r', errors='ignore' ) as entfile:

                lines = entfile.readlines()

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

                entfile.close()

            with open( map.replace( '.bsp', '.json' ), 'w' ) as jsonfile:

                jsonfile.write( '[\n' )
                FirstBlockOf = True
                FirstKeyOf = True

                for entblock in entdata:

                    if FirstBlockOf:
                        jsonfile.write( '\n' )
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

            os.remove( map.replace( '.bsp', '.ent' ) )

        elif map.endswith( '.json' ):

            with open( map, 'r' ) as jsonfile, open( map.replace( '.json', '.ent' ), 'w' ) as entfile:

                entitydata = ripent( entdata = json.load( jsonfile ) )

                for entblock in entitydata:
                    entfile.write( '{\n' )
                    for key, value in entblock.items():
                        entfile.write( f'"{key}" "{value}"\n' )
                    entfile.write( '}\n' )

            os.remove( map )
            subprocess.call( [ RIPENT, "-import", map ], stdout = open( os.devnull, "wb" ) )
            os.remove( map.replace( '.json', '.ent' ) )

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
