import markdown
import os.path
import os
import re

def buildheader():
    with open("templates/header.template.html") as f:
        return f.read()


def buildnavbar(root):
    def buildnavitem(path):
        fn, ext = os.path.splitext(os.path.basename(path))
        with open("templates/navigation/navitem.template.html") as f:
            li = f.read()
        return li.format(link="/"+path.replace("md","html"), text=fn.replace("_", " "))

    def buildnavhead(path):
        head = os.path.basename(path).replace("_", " ")
        lis = [buildnavitem(f.path) for f in os.scandir(path) if os.path.splitext(f)[1]==".md"]
        with open("templates/navigation/navhead.template.html") as f:
            navhead = f.read()
        return navhead.format(head=head, li="\n".join(lis))

    navheads = [buildnavhead(f.path) for f in os.scandir(root) if f.is_dir()]
    with open("templates/navigation/navigation.template.html") as f:
        nav = f.read()
    return nav.format(navheads="\n".join(navheads))


def buildcontent(path):
    title = os.path.splitext(os.path.basename(path))[0]
    with open(path) as f:
        markdown_text = f.read()
    content = markdown.markdown(markdown_text, extensions=["nl2br"])
    content = re.sub(r"href=\"(.*?)\.md\"", "href=\\1.html", content)
    return title, content


def buildfooter():
    with open("templates/footer.template.html") as f:
        return f.read()


def buildall(outfolder, allowed_list):
    header = buildheader()
    navbar = buildnavbar("content")
    footer = buildfooter()
    with open("templates/main.template.html") as f:
        template = f.read()
    for root, dirs, files in os.walk("content", topdown=False):
        for path in files:
            fn, ext = os.path.splitext(path)
            if ext == ".md":
                print(root+"/"+path)
                outpath = os.path.join(outfolder, root, fn+".html")
                print(outpath)
                title, content = buildcontent(os.path.join(root, path))
                os.makedirs(os.path.dirname(outpath), exist_ok=True)
                with open(outpath, "w") as outfile:
                    outfile.write(
                        template.format(
                            title=title,
                            header=header,
                            navigation=navbar,
                            footer=footer,
                            content=content
                        )
                    )
            elif ext in allowed_list:
                inpath = os.path.join(root, path)
                outpath = os.path.join(outfolder, inpath)
                os.makedirs(os.path.dirname(outpath), exist_ok=True)
                os.replace(inpath, outpath)
            else:
                print(os.path.join(root, path)+" ignored...")


buildall("public", [".pdf", ".png", ".jpg"])
