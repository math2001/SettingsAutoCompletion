# -*- encoding: utf-8 -*-

import sublime
import sublime_plugin
from os.path import sep as DS

class SettingsAutoCompletions(sublime_plugin.EventListener):

    CAPTION_TEMPLATE = '{name}\tSetting'
    COMPLETION_TEMPLATE = '"{name}": {type},'

    def get_keys(self, file):
        with open(file) as fp:
            origin_settings = sublime.decode_value(fp.read())

        settings = {}
        for origin, default_value in origin_settings.items():
            settings[origin] = default_value
        return settings

    def format_keys(self, keys):
        cls = self.__class__
        formatted_keys = []
        for name, default_value in keys.items():
            # default_value = default_value.replace('dict', '{$1}') \
            #              .replace('str', '"${1:str}"') \
            #              .replace('list', "[$1]") \
            #              .replace('bool', "${1:bool}") \
            #              .replace('int', "${1:int}")
            if isinstance(default_value, str):
                default_value = '"${1:' + default_value.replace('}', '\\}') + '}"'
            elif isinstance(default_value, bool):
                default_value = '${1:' + str(default_value).lower() + '}'
            elif isinstance(default_value, list):
                default_value = '[${1:Array}]'
            elif isinstance(default_value, dict):
                default_value = '{${1:"key": "value"}}'
            else:
                default_value = '${1:' + str(default_value) + '}'
            formatted_keys.append([cls.CAPTION_TEMPLATE.format(name=name),
                                   cls.COMPLETION_TEMPLATE.format(name=name, type=default_value)])
        return formatted_keys

    def on_post_window_command(self, window, command_name, args):
        if command_name != 'edit_settings':
            return

        keys = self.get_keys(sublime.expand_variables(args['base_file'],
                                                        window.extract_variables()))
        for view in sublime.active_window().views():
            if (DS + 'User' + DS) not in view.file_name() \
                or not view.file_name().endswith('.sublime-settings'):
                continue
            view.settings().set('settings_auto_completions', self.format_keys(keys))

    def on_query_completions(self, view, prefix, locations):
        settings_completions = view.settings().get('settings_auto_completions')
        if not settings_completions:
            return
        return settings_completions
