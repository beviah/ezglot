import os, os.path, glob, html, csv, regex as re
from collections import Counter


def cleanup(temp):

    temp = re.sub(r'\[\[Categoria.*?\]\]', '', temp, re.DOTALL)
    temp = html.unescape(temp)
    temp = re.sub(r'<noinclude>.*?</noinclude>', '', temp, re.DOTALL)
    temp = re.sub(r'<includeonly>.*?</includeonly>', '', temp, re.DOTALL)
    temp = re.sub('<[^<]+?>', '',temp)
    temp = re.sub(r'<!--.*?-->', '', temp)
    temp = re.sub(r'\/\*.*?\*\/', '', temp)

    return temp.strip()


def build_tree(data, level=1):

    tree = {}
    data = re.sub(r'{{=+([^{}]+)=+}}', r'{{\1}}', data, flags=re.MULTILINE)
    section_regex = r"(.*?)\n==+"
    sections = re.findall(section_regex, data, re.DOTALL)

    if sections:
        if sections[0].strip().strip('.').strip():
            tree[''] = sections[0].strip().strip('.').strip()

    # regex exercise
    section_regex = r"\n={%d}([^=]+)={%d}\n(.*?)(?=\n={%d}[^=]+={%d}\n|\Z)" % (
        level, level, level, level
    )
    sections = re.findall(section_regex, data, re.DOTALL)

    for section_name, section_data in sections:

        section_name = re.sub(r"\[\[([\w]+)(\|[\w]+)?\]\]", r"\1", section_name).strip()
        section_data = section_data.replace("\'\'\'",'').replace("\'\'",'').replace("\\'",'').strip().strip('.').strip()
        section_data = re.sub(r"(?<!\w)'([^']*?)'(?!\w)", r"\1", section_data)

        if not section_data:continue

        sub_level = level + 1
        if sub_level <= 5:
            subtree = build_tree(section_data, sub_level)
        else:
            subtree = section_data

        tree[section_name.strip()] = subtree

    if not sections and data.strip():
        if level == 1:
            tree[''] = build_tree(data, 2)
        else:
            tree[''] = data.strip().strip('.').strip()

    return tree


def print_tree(tree, path=None):

    if path is None:
        path = []

    # merging data from all locales to be analyzed later together.
    with open('unified.txt','a',encoding='utf-8') as w:

        for key, value in tree.items():

            new_path = path + [key.replace('=','').strip()]

            if isinstance(value, dict):
                print_tree(value, new_path)
            else:
                delimiter = " -=> "
                thing = re.sub(r'\n+\.\n+', '\n', delimiter.join(new_path).replace('-=>  -=>','-=>')+'\n'+value.strip())
                thing = thing.replace('locale -=> ','\nlocale -=> ').replace('\n\n','\n')
                w.write(thing)
                w.write('\n---------------------------------------------------------------------------')


def do_templates(fn, template):

    global reds
    
    title = temp = ''
    temps_list = []

    # find templates to replace later
    with open(fn,'r',encoding='utf-8') as f:

        for line in f:

            if '<title>'+template+':' in line:
                title = line.replace('<title>'+template+':','').replace('</title>','').strip()
            elif not title:
                continue
            else:
                if not temp and line.strip().startswith('<redirect '):
                    red = re.findall('<redirect title="(.*?)" />', line)
                    if red:red = red[0]
                    reds[title] = red.replace(template+':','')
                line = re.sub('__\w+__', '', line)
                if '<text ' in line:
                    temp = line[line.find('>')+1:]
                elif temp:
                    temp += line
                if '</text>' in line:
                    temp = temp[:temp.rfind('<')]
                    temp = cleanup(temp)
                    if '\n' not in temp and \
                       '#redirect' not in temp.lower():#hmm
                        temps_list.append((title, temp))
                        #temps[title]=temp
                    title = ''
                    temp = ''
                elif '</page>' in line:
                    title = ''

    # cleantup bad templates
    outliers = Counter([temp for title, temp in temps_list])

    for title, temp in temps_list:
        if outliers[temp]<4:
            temps[title] = temp

    todel = []

    for k in temps.keys():

        if temps[k].lower().startswith('[['+template+':'):
            try:temps[k] = temps[temps[k]].split(":")[1].replace("]]", "")
            except:todel.append(k)
        elif re.findall(r"\[\[[^\]]+:", temps[k]):
            temps[k] = re.sub(r'\[\[[^\]]+:.*?\]\]', '', temps[k], re.DOTALL)
        elif '[[:' in temps[k]:
            todel.append(k)

    for k in todel:
        if k in temps:
            del temps[k]

    return temps


try:
    #check last output for processed dumps
    with open('nohup.out') as f:
        langs = f.readlines()
except:
    langs = []

langs = [lang.strip() for lang in langs]


# get all unziped wikipedia dumps from xmls folder
files = [fpath for fpath in sorted(glob.glob("xmls/*.xml"),key=lambda file:os.stat(file).st_size,reverse=True)]
                    
for fn in files:

    if not os.path.exists(fn):
        continue

    lang = fn.split('/')[-1].replace('.xml','')

    # in rerun skip already parsed file
    if lang in langs:
        continue
    if os.path.exists(fn.replace('.xml','.tmp')):
        continue

    print(lang) # writes to nohup.out file

    temps = {}
    reds = {}

    template = 'Template'

    temps = do_templates(fn, template)

    # if no template string left, guess generic template string:
    if not temps:

        title = temp = ''
        
        with open(fn,'r',encoding='utf-8') as f:
            
            for line in f:
                
                if '<title>' in line and ':' in line:
                    template, title = line.replace('<title>','').replace('</title>','').strip().split(':', 1)
                elif not title:
                    continue
                else:
                    if '<text ' in line:
                        temp = line[line.find('>')+1:]
                    elif temp:
                        temp += line
                    if '</text>' in line:
                        temp = temp[:temp.rfind('<')]
                        ltemp = temp.lower().replace('\r','\n').replace('\n\n','\n').strip().split('\n')[0]
                        # #REDIRECT [[Template:xxx]]
                        if '#redirect [[template:'+title.lower()+']]' in ltemp:
                            break
                        elif '#redirect' in ltemp and ' [[template:' in ltemp and title in ltemp:
                            break
                        title = ''
                        temp = ''
                    elif '</page>' in line:
                        title = ''

        # don't repeat if same as original string
        if template != 'Template':
            temps = do_templates(fn, template)     

    with open(fn.replace('.xml','.tmp'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for key, value in temps.items():
            writer.writerow([key, value])

    with open(fn.replace('.xml','.red'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for key, value in reds.items():
            writer.writerow([key, value])
            
    title = temp = ''

    # normalize data, give it more uniform structure
    with open(fn,'r',encoding='utf-8') as f:
        
        for line in f:
            
            if '<title>' in line:
                
                title = line.replace('<title>','').replace('</title>','').strip()
                if ':' in title:title = ''
                
            elif not title:continue
            
            else:
                
                line = re.sub('__\w+__', '', line)
                
                if '<text ' in line:
                    temp = '\n'+line[line.find('>')+1:]
                    
                elif temp:
                    temp += line
                    
                if '</text>' in line:

                    # core logic here, and another major cleanup in the next script
                    temp = temp[:temp.rfind('<')]+'\n'
                    temp = re.sub(r'^(.*)\n= ?({{-?\w+-?}}) ?=\n(.*)$', r'\1\n=\2=\n\3', temp, flags=re.MULTILINE)
                    temp = re.sub(r'\{\{(-?[^}]+-?)\}\}', lambda m: temps.get(m.group(1), m.group()), temp)
                    temp = cleanup(temp)
                    #temps[title]=temp
                    data = temp
                    data = data.replace('\r','')
                    data = data.replace('= ','=').replace(' =','=')
                    data = data.replace('= ','=').replace(' =','=')
                    data = [d.strip() for d in data.split('\n') if d.strip()]
                    data = '\n'.join(data)
                    data = '\n'+data[data.find('='):]
                    fdata = re.sub(r'\{\{([^}]+)\}\}', lambda m: temps.get(m.group(1), m.group()), data)
                    fdata = re.sub(r'\[\[\w+:[^]]+\]+', '', fdata)
                    fdata = fdata.replace('\n=','\n\n.\n\n=').replace('=\n','=\n\n.\n\n')
                    fdata = fdata.replace('{{PAGENAME}}', title).replace('PAGENAME}}', title).replace('{{PAGENAME', title).replace('PAGENAME', title)
                    tree = build_tree(fdata)
                    treep = {'locale':{lang:{title:tree}}}
                    print_tree(treep)
                    
                    title = ''
                    temp = ''
                    data = ''
                    fdata = ''
                elif '</page>' in line:
                    title = ''



# nohup python3 -u parse_wiki.py & 
