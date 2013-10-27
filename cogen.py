#!/usr/bin/env python
import os, sys, json, distutils.core

config = json.load(open(os.path.join(os.path.dirname(__file__), 'configuration.json')))

argument = sys.argv[1]

def replace_file_contents(destination, variable, value):
  for path, dirs, files in os.walk(destination):
    for filename in files:
      file_name_temp, file_extension = os.path.splitext(filename)
      file_content = ''
      for line in open(path + '/' + filename, 'r+'):
        line_utf = line.encode('utf-8')
        file_content += line_utf.replace(variable['pattern'], value)
      file_opened = open(path + '/' + filename, 'w+')
      file_opened.write(file_content)
      file_opened.close()

def replace_file_names(destination, variable, value):
  for path, dirs, files in os.walk(destination):
    for filename in files:
      if variable['pattern'] in filename:
        os.rename(path + '/' + filename, path + '/' + filename.replace(variable['pattern'], value))

if argument[0] == '-':
  if argument == '-h':
    print 'Help text'
  elif argument == '-v':
    print 'Cogen version 1.0.0'
  elif argument == '-l':
    print 'List text'
  else:
    print 'Command not found. Type "python cogen.py -h" to see help.'
else:
  for path_to_template in config.get('paths_to_templates'):
    if not os.path.exists(path_to_template + '/' + argument):
      print 'path does not exist: ' + path_to_template
    elif not os.path.isfile(path_to_template + '/cogen.json'):
      print 'cogen.json not found'
    else:
      project_config = json.load(open(path_to_template + '/' + argument + '/cogen.json'))
      output_directory_name = raw_input('Enter folder name')
      src = path_to_template + '/' + argument
      destination = os.getcwd() + '/' + argument
      distutils.dir_util.copy_tree(src, destination)
      if project_config.get('variables'):
        for variable in project_config['variables']:
          value = raw_input(variable['name'] + ': ')
          if variable['type'] == 'all':
            replace_file_names(destination, variable, value)
            replace_file_contents(destination, variable, value)
          elif variable['type'] == 'replace':
            replace_file_contents(destination, variable, value)
          elif variable['type'] == 'rename':
            replace_file_names(destination, variable, value)
