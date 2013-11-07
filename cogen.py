#!/usr/bin/env python
import os, sys, json, distutils.core

# Get user settings.
config = json.load(open(os.path.join(os.path.dirname(__file__), 'configuration.json')))

# Define help text displayed for different flags.
text_space              = '--> '
text_help               = 'Help text'
text_list               = 'List text'
text_about              = 'About text'
text_version            = 'Cogen version: 1.0'
text_default            = 'Command not found. Type "cogen -h" to see help.'
text_invalid_path       = 'Template does not exist or "cogen.json" file is missing.'
text_replacing          = 'Starting to replace value: '
text_path_not_found     = 'Warning: path "%s" does not contain cogen.json file.'
text_cogen_not_found    = 'Warning: cogen.json file does not exist in "%s"'
text_general_not_found  = 'General variable "%s" not found.'
text_generated          = 'Template "%s" successfully generated.'
text_enter_folder_name  = 'Enter the new folder name; leave blank for default (%s): '
text_dev_processing     = 'Processing "%s"'

# Argument dictionaries.
args_out     = ['-o', '--o', '--output']
args_help    = ['-h', '--h', '--help']
args_list    = ['-l', '--l', '--list']
args_check   = ['-c', '--c', '--check']
args_version = ['-v', '--v', '--version']

# Define filetypes which will be skipped from replacing. Note: this will not
# affect changing the filenames.
files_to_skip   = config['exclude_files_from_editing']
# Folders which will be skipped from replacing checks completely.
exclude_folders_from_renaming = config['exclude_folders_from_renaming']
# Folders that will be completely excluded from all checks.
folders_to_ignore = config['folders_to_ignore']
# Folders that should be removed once the template is generated.
folders_to_delete = config['folders_to_delete']
# Folders that will be completely excluded from all checks.
folders_to_ignore = config['folders_to_ignore']

# Check if Cogen should display developer output during template generation.
show_dev_output = config['show_dev_output']

# Main function for displaying the output. For now it just spaces out all text
# with dashes/arrow so it's easier to read and see on the screen.
def output(text):
  print text_space + text

# Replace content of the file.
def replace_file_contents(destination, variable, value):
  for path, dirs, files in os.walk(destination):
    if path.split('/')[-1] not in folders_to_ignore:
      for filename in files:
        # Show developers the filename being processed.
        if show_dev_output:
          output(text_dev_processing % filename)
        # Get file extension and skip if this matches the extensions we should
        # avoid.
        file_name_temp, file_extension = os.path.splitext(filename)
        # Note: file_extension will have the dot in front of the extension name,
        # so when comparing we have to use the string starting from the second
        # character.
        if file_extension[1:] not in files_to_skip:
          file_content = ''
          for line in open(path + '/' + filename, 'r+'):
            line_utf = line.encode('utf-8')
            file_content += line_utf.replace(variable['pattern'], value)
          file_opened = open(path + '/' + filename, 'w+')
          file_opened.write(file_content)
          file_opened.close()

# Rename files.
def replace_file_names(destination, variable, value):
  for path, dirs, files in os.walk(destination):
    for filename in files:
      if path.split('/')[-1] not in folders_to_ignore:
        if variable['pattern'] in filename:
          os.rename(path + '/' + filename, path + '/' + filename.replace(variable['pattern'], value))

# Rename folders.
def rename_folders(destination, variable, value):
  for path, dirs, files in os.walk(destination):
    for dir in dirs:
      if dir not in folders_to_ignore and dir not in exclude_folders_from_renaming and variable['pattern'] in dir:
        os.rename(path + '/' + dir, path + '/' + dir.replace(variable['pattern'], value))

# Remove the first argument, which is always "cogen".
argument = sys.argv[1]

# Global flags.
if argument[0] == '-':
  if argument in args_help:
    output(text_help)
  elif argument in args_version:
    output(text_version)
  elif argument in args_list:
    output(text_list)
  else:
    output(text_general_not_found)

# Template generation.
else:
  for path_to_template in config['paths_to_templates']:
    if not os.path.exists(path_to_template + '/' + argument):
      output(text_template_not_found % path_to_template)
    elif not os.path.isfile(path_to_template + '/cogen.json'):
      output(text_cogen_not_found % path_to_template)
    else:
      project_config = json.load(open(path_to_template + '/' + argument + '/cogen.json'))
      output_directory_name = raw_input(text_enter_folder_name % argument)
      src = path_to_template + '/' + argument
      destination = os.getcwd() + '/' + argument
      distutils.dir_util.copy_tree(src, destination)
      if project_config['variables']:
        for variable in project_config['variables']:
          # Show developers the name of variable we are replacing currently.
          if show_dev_output:
            output(text_dev_replacing % value)
          value = raw_input(variable['name'] + ': ')
          # Replace all instances of the pattern: both in files and in the
          # text in the files. Note: files ending in excluded files list will
          # be skipped.
          if variable['type'] == 'all':
            replace_file_names(destination, variable, value)
            replace_file_contents(destination, variable, value)
          # Replace all instances of the pattern IN the files.
          elif variable['type'] == 'replace':
            replace_file_contents(destination, variable, value)
          # Replace all instances of the pattern in the file and folder names.
          elif variable['type'] == 'rename':
            rename_folders(destination, variable, value)
            replace_file_names(destination, variable, value)
      output(text_generated % project_config['name'])
