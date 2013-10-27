#!/usr/bin/env python
import os, sys, json, distutils.core

config = json.load(open(os.path.join(os.path.dirname(__file__), 'configuration.json')))

text_help = 'Help text'
text_list = 'List text'
text_about = 'About text'
text_version = 'Cogen version: 1.0'
text_default = 'Command not found. Type "cogen -h" to see help.'
text_invalid_path = 'Template does not exist or "cogen.json" file is missing.'
text_replacing = 'Starting to replace value: '
text_path_not_found = 'Warning: path "%s" does not contain cogen.json file.'
text_cogen_not_found = 'Warning: cogen.json file does not exist in "%s"'
text_general_not_found = 'General variable "%s" not found.'
text_generated = 'Template "%s" successfully generated.'

args_out = ['-o', '--o', '--output']
args_help = ['-h', '--h', '--help']
args_list = ['-l', '--l', '--list']
args_check = ['-c', '--c', '--check']
args_version = ['-v', '--v', '--version']

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
  if argument in args_help:
    print text_help
  elif argument in args_version:
    print text_version
  elif argument in args_list:
    print text_list
  else:
    print text_general_not_found
else:
  for path_to_template in config.get('paths_to_templates'):
    if not os.path.exists(path_to_template + '/' + argument):
      print text_template_not_found % path_to_template
    elif not os.path.isfile(path_to_template + '/cogen.json'):
      print text_cogen_not_found % path_to_template
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
      print text_generated % project_config['name']
