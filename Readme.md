# Mydrive 

 

Mydrive is a python and javascript based website using Django API to store files and directories on the server and optionally make them public for other users to be accessed.

 

Files and direcorties are stored in Media which was written automatically by Settings.py file:

```python 
MEDIA_URL = '/media/'
``` 


## How it works 

Once an user(A) signup , Pyhton will  create a root directory using his username but first , must check if there is not a directory that has that username , all files uploaded and directories created will be saved in this root directory (username).

User have many functions to manage his own directory  , he can move and copy , rename , delete , download . and make his files and dirs public or private .

User can set the privacy of his content public or private .

##### Private
By default, the content is hidden from search resault , and the owner just use this file or dir as a storage or backup .

##### Public
Other users could find any public file by tapping the key word "file name" on search bar. 


#### Settings

In settings page he can allow/disallow downloading , also make his username appear/hidden in search resault .


#### Search

if user(A) post a file and name it "myfile" , and another connected user(B) tape in search bar "myfile"  , as resault all files whose name contains "myfile" AND they are pulblic, will be shown. Now user(B) can download them depend the settings of privacy for user(A) .


## Tree of mydrive application

for the tree files of app "mydrive"

```bach 

├── admin.py  			
├── apps.py
├── __init__.py
├── models.py			
├── static
│   └── mydrive
│       ├── all.min.css		#css file for font-awsome , it contains majority of icons.
│       ├── index.js		#main file of javascript , it contains all functions of mydrive app.
│       ├── jquery.js		#Jquery , a javascript Library , Write less do more.
│       ├── styles.css		#main stylesheet file of mydrive app.
│       └── webfonts		#font that used by fontawsome.
├── templates
│   └── mydrive
│       ├── index.html		#index page where user manage his files and dirs.
│       ├── layout.html		#Layout , include it in index.html and settings.html and search.html to avoid re-tape same html.
│       ├── login.html		
│       ├── register.html	
│       ├── search.html		#search page to show resault of search bar .
│       └── settings.html	#settings where user can change settings of his content.
├── tests.py			
├── urls.py			#it contains urls of mydrive application to redirect user to : index.html , login.html , register.html , search.html , settings.html.
└── views.py			#Main file of Pythons functions , it has all the code to treat "mydrive" data from server side.
```

 
**admin.py:** contains models to access them from admin interface.

**models.py:** contains Models: User , Settingsuser , Content , more detail in DataBase section .

**index.js:** main file of javascript , it contains all functions of mydrive app including:

*global var "ActuelDir"*  : it will stock the actual path.
	
**functions that call server requests:**
		 
*"getDir()":* gets content of a specific path using ActuelDir => route => /getDir.
		 
*"uploadfile()":* uploads multiple files => route => /setFiles.
		 
*"goTo()":* triggers when user click on a directory, it will call getDir() and update ActuelDir.
		 
*"creatDir()":* to create new directory 
		 
*"exerenameDir()":* to rename directory
		 
*"deleteDir(ele)":* to delete directory
		 
*"copymoveDir(functionIs, from, ele)":* performs copy and move directory ; it has 3 parameters:
		 	{functionIs} be one of 2 values "copy" or "move".
		 	{from}: the directory name , 
		 	{ele} : element clicked on
		 	 
*"setprivercy()":* Set public/private of a file or a directory => route => /setprivercy.
		  
*note that "/setDir" could has 4 parameters :*   
		 	{funct} takes "add" | "rename" | "delete" as value.
		 	{namedir}: name of selected directory  .
		 	{R}: var ActuelDir .  
		 	{olddir} : Optional parameter to get previous selected directory.
		 
**functions that affect view(html/css) in client side:**
	
*"addFiles(getFiles, path)":* add "div" of file(s) in the current path , {getFiles}: informations of file , {path} : current path.

*"adddirName()" :*  add div contains input of directory name.
	         
*"reNameDir(ele)" :* switch from read to editable of the directory name.

*"callTocopymoveDir(ele)":* show box of "copy|move" and "past".
		 
*"downloadDir(ele)" :* redirect to a link for downloading , it will trigger download(request) in view.py
		 
	
		 
**views.py :** main file of mydrive app , it contains all functions of mydrive app including:
		index(request) : method that called from url.py, path index, it checks the user's existing root directory to redirect to index.html otherwise it will redirect to the registration page .
		
*settingsUser(request):* get form of settings.html .
		
*search(request):* get request from search bar to show resault in search.html.
		
*getDir(request):* called by getDir() function located in index.js , by passing path of dir as parameter which will trigger getReprtoire(username,path) function .
		
*getReprtoire(username,path):* returns the contents of a specific directory.
		
*setDir(request):* called by setDir function from index.js , this function performed on files and directories including: add, rename, move, copy, delete. this is the complicated method on this project .
		
*addCopyinNameFile(namefile) :* this function helps to rename duplicate files by adding "-copy" or "-copy-copy"  ...etc.
		
*download(request):* to manage download directory using zip and files ,called by downloadDir(ele) from index.js.

*setprivercy(request):*  to set public/private of a file or a directory, called by setprivercy() from index.js
		
*setFiles(request):* for uploading files.
		
*checkAdminPath(username,path):* check if the root directory of an user belong to connected user.
		
*login_view(request) :* called when the user logs in to redirect to the index. 
		
*logout_view(request):* called when a user logs out to redirect to the index, then to the login page.
		
*register(request):* called when the user registers to redirect to the index and create the user's root directory. 
		

**url.py:** it contains all route of mydrive.	
		

## DataBase

**Content** Model : it contains 4 fields : owner , path , file , privacy .

*owner :* ForeignKey of User model.

*path :* it contains the path of directory , the path starts with "/username/.*".

*file :* if the path is a file, this column will contain a file name, otherwise "null".

*privecy :* by default "private" otherwise "public" .


**Settingsuser** Model : it contains 3 fields : ownerSettings , allowusername , allowdownload.

*ownerSettings :*  ForeignKey of User model.

*allowusername :* Bool field by default "True" , check if users can see the "username" of the owner's file (in case this file is public).

*allowdownload :*  Bool field by default "True" , check if users can download the file (in case that file is public).


**User** Model : from django.contrib.auth.models , AbstractUser model.

## Requirements 

 
I used magic to get the exact format of file when user click on download.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install magic. 


 

```bash 

pip3 install python-magic 

``` 



## Usage 

```bach
cd /to/path/drive
python3 manage.py makemigrations mydriver
python3 manage.py migrate --run-syncdb
python3 manage.py runserver
```

In case you are using Python 3 , change python to python3

 

## Contributing 

I would like to thanks Brian Yu for his amazing tutoriels and David J.Malan and Harvard university and Edx platform , i really appreciate your time , thank you.
 

## License 

[MIT](https://choosealicense.com/licenses/mit/) 

