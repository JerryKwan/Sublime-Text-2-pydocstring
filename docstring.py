# -*- coding: utf-8 -*-
'''
Created on 2012-05-25 14:38
@summary: a python docstring plugin for sublime text 2
@author: JerryKwan
@contact: Jinzhong.Guan@gmail.com
'''


import sublime
import sublime_plugin
import string
import datetime
import getpass
import os.path

def construct_module_docstring():
    '''
    @summary: construct the module docstring
    '''
    docstring = "# -*- coding: utf-8 -*-\n"
    docstring += "'''\n"
    docstring += "Created on %s\n"
    docstring += "@summary: \n"
    docstring += "@author: %s\n"
    docstring += "'''\n\n"
    docstring = docstring % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), getpass.getuser())
    return docstring


def construct_docstring(declaration, indent = 0):
    '''
    @summary: construct docstring according to the declaration
    @param declaration: the result of parse_declaration() reurns
    @param indent: the indent space number
    '''
    docstring = ""
    try:
        typename, name, params = declaration
        lines = []
        lines.append("'''\n")
        lines.append("@summary: \n")
        # lines.append("\n")
        if typename == "class":
            pass
        elif typename == "def":
            if len(params):
                for param in params:
                    lines.append("@param %s:\n"%(param))
                # lines.append("\n")
            lines.append("@result: \n")
        lines.append("'''\n")

        for line in lines:
            docstring += " " * indent + line

    except Exception, e:
        print e

    return docstring


def get_declaration(view, point):
    '''
    @summary: get the whole declaration of the class/def before the specified point
    @return: (True/False, region)
            True/False --- if the point in a declaration region
            region --- region of the declaration
    '''
    flag = False
    declaration_region = sublime.Region(0, 0)

    b_need_forward = False
    b_need_backward = False


    declaration = ""
    line = view.line(point)
    begin_point = line.begin()
    end_point = line.end()
    while True:
        if begin_point < 0:
            print "can not find the begin of the declaration"
            flag = False
            break
        line = view.line(begin_point)
        line_contents = view.substr(line)
        words = line_contents.split()
        if len(words) > 0:
            if words[0] in ("class", "def"):
                flag = True
                begin_point = line.begin()
                end_point = line.end()
                break
        # get previous line
        begin_point = begin_point - 1

    if flag:
        # check from the line in where begin_point lives
        line = view.line(end_point)
        line_contents = view.substr(line).rstrip()
        while True:

            if end_point > view.size():
                print "can not find the end of the declaration"
                flag = False
                break

            if (len(line_contents) >= 2) and (line_contents[-2:] == "):"):
                print "reach the end of the declaration"
                flag = True
                end_point = line.begin() + len(line_contents) - 1
                break
            # get next line
            line = view.line(end_point + 1)
            end_point = line.end()
            line_contents = view.substr(line).rstrip()

    # check valid
    if end_point <= begin_point:
        flag = False

    # check it again, trip unnessary lines
    if flag:
        declaration_region = sublime.Region(begin_point, end_point)

    return (flag, declaration_region)

def parse_declaration(declaration):
    '''
    @summary: parse the class/def declaration
    @param declaration: class/def declaration string
    @result:
        (typename, name, params)
        typename --- a string specify the type of the declaration, must be 'class' or 'def'
        name --- the name of the class/def
        params --- param list
    '''
    def rindex(l, x):
        index = -1
        if len(l) > 0:
            for i in xrange(len(l) - 1, -1, -1):
                if l[i] == x:
                    index = i
        return index


    typename = ""
    name = ""
    params = []

    tokens = {")": "(",
                "]": "[",
                "}": "{",
                }

    # extract typename
    declaration = declaration.strip()
    if declaration.startswith("class"):
        typename = "class"
        declaration = declaration[len("class"):]
    elif declaration.startswith("def"):
        typename = "def"
        declaration = declaration[len("def"):]
    else:
        typename = "unsupported"

    # extract name
    declaration = declaration.strip()
    index = declaration.find("(")
    if index > 0:
        name = declaration[:index]
        declaration = declaration[index:]
    else:
        name = "can not find the class/def name"

    # process params string
    # the params string are something like "(param1, param2=..)"
    declaration = declaration.strip()
    print "\nparams string is ", declaration
    if (len(declaration) >= 2) and (declaration[0] == '(') and (declaration[-1] == ')'):
        # continue process
        declaration = declaration[1:-1].strip()

        stack = []
        for c in declaration:
            if c in string.whitespace:
                if len(stack) > 0:
                    if stack[-1] in string.whitespace:
                        # previous char is whitespace too
                        # so we will discard current whitespace
                        continue
                    else:
                        # push stack
                        stack.append(" ")
                else:
                    # discard leading whitespaces
                    continue
            else:

                if c in tokens.keys():
                    # find the corresponding token
                    index = rindex(stack, tokens[c])
                    print "c = %s, index = %s"%(c, index)
                    if index > 0:
                        # delete all of the elements between the paired tokens
                        stack = stack[:index]
                else:
                    # push stack
                    stack.append(c)

        tmp = "".join(stack)
        print "\nstack is: ", tmp
        # split with ,
        stack = tmp.split(",")
        print "stack is: ", "".join(stack)
        params = []
        for w in stack:
            w = w.strip()
            if w == "self":
                # skip self parameter
                continue
            index = w.find("=")
            if index > 0:
                params.append(w[:index].strip())
            else:
                params.append(w)
    else:
        params = []

    return(typename, name, params)


class DocstringCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        filename = self.view.file_name()
        _, ext = os.path.splitext(filename)
        # check if python file?
        if not ext == ".py":
            return
        # get the content of the line
        for region in self.view.sel():
            # print region.begin()
            if region.empty():
                line = self.view.line(region)
                previous_region = sublime.Region(0,line.begin())
                previous_contents = self.view.substr(previous_region)
                if len(previous_contents.strip()) == 0:
                    print "at the begin of the file so we can insert module docstring"
                    self.view.insert(edit, 0, construct_module_docstring())

                else:
                    print "not begin of the file"

                tab_size = self.view.settings().get("tab_size", 4)
                # if tab_size < 4:
                #     tab_size = 4
                print "tab_size = ", tab_size
                flag, declaration_region = get_declaration(self.view, line.begin())
                print "declaration_region begin = %s, end = %s"%(declaration_region.begin(),
                    declaration_region.end())
                declaration = self.view.substr(declaration_region)
                print "is_declaration: %s\ndeclaration:%s"%(flag, declaration)
                if flag:
                    # valid declaration
                    result = parse_declaration(declaration)
                    # calculate docstring indent
                    indent = 0
                    try:
                        name = result[1]
                        print "declaration = %s, name = %s"%(declaration, name)
                        index = declaration.find(name)
                        if index >=0:
                            for i in xrange(index):
                                if declaration[i] == "\t":
                                    indent += tab_size
                                else:
                                    indent += 1
                        # calculate the real indent
                        if indent % tab_size :
                            indent = (indent / tab_size) * tab_size
                        print "indent = %s"%(indent)
                        docstring = construct_docstring(result, indent = indent)
                        print "docstring is: \n%s" %(docstring)
                        # insert class/def docstring
                        # print "row = %s, col = %s"%(self.view.rowcol(declaration_region.end()))
                        self.view.insert(edit, declaration_region.end() + 2, docstring)
                    except Exception, e:
                        print e



