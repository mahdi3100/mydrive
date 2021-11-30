from django.contrib.auth import authenticate, login, logout
from django.db import connection,IntegrityError
from django.db.models import F

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
#from .models import User

from django.conf import settings

from .models import *
import os
import shutil
import re
from django.core.files.storage import default_storage

import zipfile
from io import BytesIO#import StringIO
from distutils.dir_util import copy_tree
import magic

def index(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    #GET DIR ADMIN FROM ROOT WWW
    dirroot= os.path.join(settings.MEDIA_ROOT,request.user.username)

    #IF DOES NOT EXIST REDIRECT
    if not os.path.isdir(dirroot):
        return HttpResponseRedirect(reverse("register"))

    return render(request, "mydrive/index.html")


@login_required(login_url='/login')
@csrf_exempt
def settingsUser(request):
    if request.method == "POST":

        #PASS OBJECT TO FORM TO CHECK OR UNCHECK CHECKBOX
        getSettingUser = Settingsuser.objects.get(ownerSettings=request.user.id)
        form = Newsettingsform(request.POST,idUser=None,instance=getSettingUser)

        if form.is_valid():

           form.save()
           return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "mydrive/settings.html", {
            "form": Newsettingsform(idUser=request.user.id)
        })

class Newsettingsform(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        self.idUser = kwargs.pop('idUser')

        super(Newsettingsform,self).__init__(*args,**kwargs)
        if self.idUser != None:
            getSettingUser = Settingsuser.objects.get(ownerSettings=self.idUser)
            self.fields['allowdownload'].initial=getSettingUser.allowdownload
            self.fields['allowusername'].initial=getSettingUser.allowusername

    class Meta:
        model = Settingsuser
        fields = ['allowdownload', 'allowusername']
        labels = {
        "allowdownload": "Allow other users download your public files ",
        "allowusername":"Allow other users see your username"
        }


def search(request):

        getValueSearch = request.GET.get("q","")

        if len(getValueSearch) < 3:
            return  render(request, "mydrive/search.html",{"error":"You search string must be greater than 3 chars"})

        getPaths = Content.objects.select_related().filter(file__contains=getValueSearch,privercy="public").all()

        #CHECK IF PATH EXIST IN BDD
        if not getPaths:
            return  render(request, "mydrive/search.html",{"error":"No file's match your search"})

        files = []

        #GET DATA FROM BDD USING getPaths Object
        for i in range(len(getPaths)):
            getSettingsUser = Settingsuser.objects.select_related().get(ownerSettings=getPaths[i].owner.id)
            allowdownload = getSettingsUser.allowdownload
            allowusername = getSettingsUser.allowusername
            username = None
            if allowusername:
                username=getPaths[i].owner.username
            download= None
            if allowdownload:
                download = allowdownload

            getExtention = getPaths[i].file[getPaths[i].file.rfind(".")+1:]

            files.append({"path":getPaths[i].path,"download":download,"username":username,"name":getPaths[i].file,"format":getExtention})


        return  render(request, "mydrive/search.html",{"files":files,"allowdownload":allowdownload})




def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


@csrf_exempt
def getDir(request):
    data = json.loads(request.body)
    getParameterRepertoire= data.get("R", "")
    return JsonResponse({"repertoir":getReprtoire(request.user.username,getParameterRepertoire)})


#THIS FUNCTION IS FOR COPY MOVE DELETE RENAME (FILES & DIRS) , ADD DIR
@login_required(login_url='/login')
@csrf_exempt
def setDir(request):

    data = json.loads(request.body)
    getCurrentDir = data.get("R", "")
    getFunction = data.get("funct", "")


    if getFunction == "add":#ONLY DIRS

        getNameDir = data.get("namedir","")
        if getNameDir == "" or bool(re.match(r"(([a-zA-Z])+[0-9]*)(\s{1,2}[a-zA-Z0-9]+){0,2}\s*$" ,getNameDir )) == False:
            return JsonResponse({"error":1,"txt":"Name dir should not have specials chars"})



        allPath = os.path.join(settings.MEDIA_ROOT,getCurrentDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir

        if not os.path.exists(allPath):
            return JsonResponse({"error":1,"txt":"This path does not exist"})

        allPath = os.path.join(allPath,getNameDir)

        try:
            os.makedirs(allPath)
        except FileExistsError:
            os.makedirs(allPath+"-copy")
            getNameDir = getNameDir+"-copy"

        setToBdd = Content(None,request.user.id,getCurrentDir+"/"+getNameDir,None,"private")
        setToBdd.save()

        return JsonResponse({"error":0})

    if getFunction == "rename":

        getNameDir = data.get("namedir","")
        getOldDir = data.get("olddir","")


        if getOldDir == "" or getNameDir == "" or bool(re.match(r"(([a-zA-Z\-])+[0-9]*)(\s{1,2}[a-zA-Z0-9\-]+){0,2}\s*$" ,getNameDir )) == False:
            return JsonResponse({"error":1,"txt":"Name dir should not have specials chars"})

        getCurrentDir = getCurrentDir+"/"+getOldDir

        if checkAdminPath(request.user.username,getCurrentDir) == False:
            return JsonResponse({"error":1,"txt":"You must be the owner"});


        oldDirPath = os.path.join(settings.MEDIA_ROOT,getCurrentDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir

        if not os.path.exists(oldDirPath):
            return JsonResponse({"error":1,"txt":"This path does not exist"})

        if os.path.isfile(oldDirPath):
            getExtention = getOldDir[getOldDir.rfind("."):]
            getNameDir = getNameDir+getExtention
            getMainDirWithoutFile = getCurrentDir[:getCurrentDir.rfind("/")]
            Content.objects.filter(path=getMainDirWithoutFile,file=getOldDir).update(file=getNameDir)
        else:#FOR DIRS
            getMainDirWithoutFile = getCurrentDir[:getCurrentDir.rfind("/")]
            Content.objects.filter(path=getCurrentDir).update(path=getMainDirWithoutFile+"/"+getNameDir)






        RemoveAcuteldirFromPath = getCurrentDir[:getCurrentDir.rfind("/")+1]
        newPath = RemoveAcuteldirFromPath+"/"+getNameDir
        newPath = os.path.join(settings.MEDIA_ROOT,newPath[1:])



        os.rename(oldDirPath,newPath)
        return JsonResponse({"error":0})

    if getFunction == "delete":
        getNameDir = data.get("namedir","")


        getContentDir = getCurrentDir+"/"+getNameDir
        getDirPath = os.path.join(settings.MEDIA_ROOT,getContentDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir

        if checkAdminPath(request.user.username,getCurrentDir) == False:
            return JsonResponse({"error":1,"txt":"You must be the owner"})


        #PREVENT USER TO DELETE HIS OWN ROOT DIR
        if len(re.findall(rf"{request.user.username}" ,getContentDir, re.IGNORECASE)) > 1:
            return JsonResponse({"error":1,"txt":"We can not delete you root dir !"})


        if not os.path.exists(getDirPath):
            return JsonResponse({"error":1,"txt":"This path does not exist"})



        if os.path.isdir(getDirPath):

            shutil.rmtree(getDirPath)
            Content.objects.filter(path=getContentDir).delete()

        else:#FOR FILES
            os.remove(getDirPath)
            print(getContentDir+" , "+getNameDir)
            Content.objects.filter(path=getCurrentDir,file=getNameDir).delete()

        return JsonResponse({"error":0})

    if getFunction == "copy":
        getFromNameDir = data.get("fromnamedir","")

        getFromNameDirBDD = getCurrentDir


        getFromDirPath = os.path.join(settings.MEDIA_ROOT,getFromNameDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir


        getCopyDirPath = os.path.join(settings.MEDIA_ROOT,getCurrentDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir

        print(getFromDirPath)
        if not os.path.exists(getCopyDirPath):
            return JsonResponse({"error":1,"txt":"aaaThis path does not exist"})

        print(getFromDirPath)
        if not os.path.exists(getFromDirPath):
            return JsonResponse({"error":1,"txt":"bbbThis path does not exist"})

        if os.path.isdir(getFromDirPath):
            getOnlyFromDirName= getFromNameDir[getFromNameDir.rfind("/")+1:]

            getAllCopyPathName = getCopyDirPath+"/"+getOnlyFromDirName
            try:
                os.makedirs(getAllCopyPathName)
            except FileExistsError:
                os.makedirs(getAllCopyPathName+"-copy")
                getOnlyFromDirName = getOnlyFromDirName+"-copy"
                getAllCopyPathName = getCopyDirPath+"/"+getOnlyFromDirName




            copy_tree(getFromDirPath,getAllCopyPathName)

            GetDirTOForBDD = getCurrentDir+"/"+getOnlyFromDirName

            setToBdd = Content(None,request.user.id,GetDirTOForBDD,None,"private")
            setToBdd.save()

            _ , filenames = default_storage.listdir(f"{getAllCopyPathName}")
            for file in filenames:
                setToBdd = Content(None,request.user.id,GetDirTOForBDD,file,"private")
                setToBdd.save()

            return JsonResponse({"error":0,"type":"dir","name":getOnlyFromDirName})

        else:#FOR FILES

            getOnlyFromDirFileName= getFromNameDir[getFromNameDir.rfind("/")+1:]


            getAllCopyPathName = getCopyDirPath+"/"+getOnlyFromDirFileName


            _ , filenames = default_storage.listdir(f"{getCopyDirPath}")

            checkAllname = False
            while checkAllname == False:
                found = False
                for file in filenames:
                    if file == getOnlyFromDirFileName:
                        getAllCopyPathName = addCopyinNameFile(getAllCopyPathName)
                        getOnlyFromDirFileName = addCopyinNameFile(getOnlyFromDirFileName)
                        print("will break")
                        found = True
                if found == False:
                    checkAllname = True





            try:
                shutil.copyfile(getFromDirPath,getAllCopyPathName)
            except shutil.SameFileError:
                getAllCopyPathName = addCopyinNameFile(getAllCopyPathName)
                getOnlyFromDirFileName = addCopyinNameFile(getFromNameDirBDD)
                shutil.copyfile(getFromDirPath,getAllCopyPathName)



            getExtention = getOnlyFromDirFileName[getOnlyFromDirFileName.rfind(".")+1:]


            getCopyDirPathWithoutMedia = getCopyDirPath[getCopyDirPath.rfind("/media")+7:]


            getUsernamePathDir = getFromNameDir[:getFromNameDir.rfind("/")]




            setToBdd = Content(None,request.user.id,getCurrentDir,getOnlyFromDirFileName,"private")
            setToBdd.save()

            return JsonResponse({"error":0,"path":getCopyDirPathWithoutMedia,"type":getExtention,"name":getOnlyFromDirFileName})



    if getFunction == "move":
        getFromNameDir = data.get("fromnamedir","")

        getFromNameDirBDD = getCurrentDir

        getFromDirPath = os.path.join(settings.MEDIA_ROOT,getFromNameDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir


        getCopyDirPath = os.path.join(settings.MEDIA_ROOT,getCurrentDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir

        if checkAdminPath(request.user.username,getCurrentDir) == False:
            return JsonResponse({"error":1,"txt":"You must be the owner"})

        if not os.path.exists(getCopyDirPath):
            return JsonResponse({"error":1,"txt":"This path does not exist"})

        if not os.path.exists(getFromDirPath):
            return JsonResponse({"error":1,"txt":"This path does not exist"})


        if os.path.isdir(getFromDirPath):

            getOnlyFromDirName= getFromNameDir[getFromNameDir.rfind("/")+1:]

            getAllPathTo = getCopyDirPath+"/"+getOnlyFromDirName
            getDirToForBDD = None


            getPathTo = getCopyDirPath+"/"+getOnlyFromDirName
            try:
                os.makedirs(getAllPathTo)
                getDirToForBDD = getFromNameDirBDD+"/"+getOnlyFromDirName
            except FileExistsError:
                #os.makedirs(getAllPathTo+"-copy")
                return JsonResponse({"error":1,"txt":"We can not move dir in the same path"})


            print(getFromDirPath)
            print(getPathTo)
            copy_tree(getFromDirPath,getPathTo)
            shutil.rmtree(getFromDirPath)


            Content.objects.filter(path=getFromNameDir).delete()

            setToBdd = Content(None,request.user.id,getDirToForBDD,None,"private")
            setToBdd.save()

            _ , filenames = default_storage.listdir(f"{getAllPathTo}")
            Content.objects.filter(path=getFromNameDir,file__in=filenames).delete()
            for file in filenames:
                setToBdd = Content(None,request.user.id,getDirToForBDD,file,"private")
                setToBdd.save()

            return JsonResponse({"error":0,"type":"dir","name":getOnlyFromDirName})

        else:#FOR FILES

            getOnlyFromDirFileName= getFromNameDir[getFromNameDir.rfind("/")+1:]

            getAllCopyPathName = getCopyDirPath+"/"+getOnlyFromDirFileName

            _ , filenames = default_storage.listdir(f"{getCopyDirPath}")


            getOldNameIfFound = getOnlyFromDirFileName
            checkAllname = False
            while checkAllname == False:
                found = False
                for file in filenames:
                    if file == getOnlyFromDirFileName:
                        getAllCopyPathName = addCopyinNameFile(getAllCopyPathName)
                        getOnlyFromDirFileName = addCopyinNameFile(getOnlyFromDirFileName)
                        print("will break")
                        found = True
                if found == False:
                    checkAllname = True

            try:
                shutil.copyfile(getFromDirPath,getAllCopyPathName)
            except shutil.SameFileError:
                getAllCopyPathName = addCopyinNameFile(getAllCopyPathName)
                getOnlyFromDirFileName = addCopyinNameFile(getOnlyFromDirFileName)


                shutil.copyfile(getFromDirPath,getAllCopyPathName)
                pass


            getExtention = getOnlyFromDirFileName[getOnlyFromDirFileName.rfind(".")+1:]
            os.remove(getFromDirPath)


            Content.objects.filter(path=getCurrentDir,file=getOldNameIfFound).delete()

            setToBdd = Content(None,request.user.id,getCurrentDir,getOnlyFromDirFileName,"private")
            setToBdd.save()


            getCopyDirPathWithoutMedia = getCopyDirPath[getCopyDirPath.rfind("/media")+7:]
            return JsonResponse({"error":0,"path":getCopyDirPathWithoutMedia,"type":getExtention,"name":getOnlyFromDirFileName})


        return JsonResponse({"error":0,"name":getOnlyFromDirName})

    else:#UNKNOWN FUNCTION
        return JsonResponse({"error":1,"txt":"Function does not exist !"})


#FUNCTION TO GENERATE "COPY" in NAMES FILE & DIRS
def addCopyinNameFile(filename):

    #CASES WHERE FILE NAME DOES NOT HAVE FORMAT - LINUX FILES
    if filename.rfind(".") == -1:
        return filename+"-copy"

    getextesion = filename[filename.rfind("."):]
    getname = filename[:filename.rfind(".")]+"-copy"

    return getname+getextesion


@login_required(login_url='/login')
def download(request):

    getCurrentDir = request.GET.get("path","");
    getNameDir = request.GET.get("dir","");



    getContentDir = getCurrentDir
    getCurrentDir = getCurrentDir+"/"+getNameDir
    getDirPath = os.path.join(settings.MEDIA_ROOT,getCurrentDir[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir

    if checkAdminPath(request.user.username,getCurrentDir) == False:

        getUsername = getContentDir[1:]
        getUsername = getUsername[:getUsername.find("/")]

        print(f"=>{getUsername}")
        getOwnerPath = Content.objects.select_related().filter(path=getContentDir,file=getNameDir,owner__username=getUsername)

        if not getOwnerPath:

            return HttpResponseRedirect(reverse("index"))
        getSettingOwner = [Settingsuser.objects.filter(ownerSettings=ownerUser.owner).all() for ownerUser in getOwnerPath]
        allowdownload =getSettingOwner[0][0].allowdownload
        if allowdownload == False:
            return HttpResponseRedirect(reverse("index"))



    if os.path.isfile(getDirPath):
        readFile = open(getDirPath, 'rb').read()
        mime = magic.Magic(mime=True)

        response = HttpResponse(readFile)
        response['Content-Type'] = mime.from_file(getDirPath)
        response['Content-Disposition'] = 'attachment; filename='+getNameDir
        return response

    if not os.path.exists(getDirPath):
        print("sssssssssssssssss")
        return HttpResponseRedirect(reverse("index"))

    zipdir = getNameDir+"-Compress"
    zip_filename = "%s.zip" % zipdir

    # Open StringIO to grab in-memory ZIP contents
    sMemory=BytesIO()# sMemory = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(sMemory, "w")

    _ , filenames = default_storage.listdir(f"{getDirPath}")

    for file in filenames:
        # Calculate path for file in zip
        #_, fname = os.path.split(file)
        toFile = getDirPath+"/"+file
        zip_path = os.path.join(zipdir, file)

        # Add file, at correct path
        zf.write(toFile, zip_path)

    # Must close zip for all contents to be written
    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(sMemory.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

@login_required(login_url='/login')
@csrf_exempt
def setprivercy(request):
    data = json.loads(request.body)
    getCurrent= data.get("R", "")
    getElement= data.get("nameDirFile", "")
    getPrivercy =data.get("privercy", "")

    if getPrivercy != "public" and getPrivercy != "private":
        return JsonResponse({"error":1,"txt":"Please try again !"})

    getPath = getCurrent+"/"+getElement
    getAllMediaPath = os.path.join(settings.MEDIA_ROOT,getPath[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir


    if checkAdminPath(request.user.username,getPath) == False:
        return JsonResponse({"error":1,"txt":"You must be the owner"})

    if not os.path.exists(getAllMediaPath):
        return JsonResponse({"error":1,"txt":"This path does not exist"})

    if os.path.isdir(getAllMediaPath):

        getprivercy = Content.objects.filter(path=getPath).update(privercy=getPrivercy)
        if not getprivercy:
            return JsonResponse({"error":1,"txt":"Please try again !"})
        else:
            return JsonResponse({"error":0,"type":"dir"})



    if os.path.isfile(getAllMediaPath):
        try:
            getprivercy = Content.objects.get(path=getCurrent,file=getElement)

            getprivercy.privercy = getPrivercy
            getprivercy.save()

            if getPrivercy == "public":
                getprivercy = Content.objects.filter(path=getCurrent,file__isnull=True).update(privercy=getPrivercy)


            return JsonResponse({"error":0,"type":"file"})
        except Content.DoesNotExist:
            return JsonResponse({"error":1,"txt":"Please try again !"})

def getReprtoire(username,namePath):

    if not namePath:
        namePath= os.path.join(settings.MEDIA_ROOT,username)
        pathForBdd = "/"+username

    else:

        pathForBdd = namePath
        namePath = os.path.join(settings.MEDIA_ROOT,namePath[1:])#getCurrentDir => /username , to join with media , have remove "/" in getCurrentDir


    dirsInfo = []
    filesInfo = []


    if os.path.exists(namePath):#"/username"

        dirs , filenames = default_storage.listdir(f"{namePath}")

        if dirs:
            for dir in dirs:
                getprivercy = Content.objects.filter(path=pathForBdd+"/"+dir,file__isnull=True).values("privercy")
                dirsInfo.append({"type":"dir","name":dir,"privercy":getprivercy[0]["privercy"]})#size , path , get_created_time , default_storage methods

        if filenames:
            for file in filenames:

                getprivercy = Content.objects.filter(path=pathForBdd,file=file).values("privercy")


                getExtention = file[file.rfind(".")+1:]
                filesInfo.append({"type":getExtention,"name":file,"privercy":getprivercy[0]["privercy"]})





        backward = True
        getPathUser = namePath[namePath.find('media')+6:]
        if getPathUser == username:
            backward = False
        return {"backward":backward,"path":namePath[namePath.find('media')+5:]  ,"dirs":dirsInfo,"files":filesInfo}
    return False


@csrf_exempt
@login_required(login_url='/login')
def setFiles(request):
    #dir= os.path.join(settings.MEDIA_ROOT,"test")

    if request.method == "POST":


        if request.FILES and request.POST:

            myfileSS = request.FILES.getlist('myFiles')




            getDir = request.POST["dir"]

            if checkAdminPath(request.user.username,getDir) == False:
                return JsonResponse({"error":1,"txt":"You must be the owner"})

            namePath= os.path.join(settings.MEDIA_ROOT,getDir[1:])

            if not os.path.exists(namePath):#"/username"
               return JsonResponse({"error":1,"txt":"This path does not existe"})


            fs = FileSystemStorage(namePath)
            filesInfo = []

            _ , filenames = default_storage.listdir(f"{namePath}")



            for myfile in myfileSS:

                for file in filenames:
                    if myfile.name == file:
                        myfile.name = addCopyinNameFile(myfile.name)


                filename = fs.save(myfile.name, myfile)

                getExtention = filename[filename.rfind(".")+1:]
                filesInfo.append({"name":filename,"type":getExtention})

                setToBdd = Content(None,request.user.id,getDir,myfile.name,"private")
                setToBdd.save()

            return JsonResponse({"error":0,"files":filesInfo,"path":getDir})

        else:
            return JsonResponse({"error":1,"txt":"Method must be FILES "})
    else:
        return JsonResponse({"error":1,"txt":"Method must be POST"})


#CHECK IF PATH START WITH /USERNAME
def checkAdminPath(username,path):

    if bool(re.search(rf"^\/{username}.*" ,path, re.IGNORECASE))==True:
        return True
    else:
        return False



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)


        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session["username"] = username
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "mydrive/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "mydrive/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "mydrive/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            request.session["username"] = username
            user.save()

            settingsuser = Settingsuser(ownerSettings=user, allowdownload=True, allowusername=True)
            settingsuser.save()

            dir= os.path.join(settings.MEDIA_ROOT,username)
            if not os.path.exists(dir):
                os.makedirs(dir)

        except IntegrityError:
            return render(request, "mydrive/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mydrive/register.html")
