var ActuelDir = "";
$(document).ready(function() {
  getDir();
});

$(document).on("click", ".privercycancel", function() {
  $("#formprivercy").hide();
})
$(document).on("click", ".iconprivercy", function() {

  var getElement = $(this).parent().find("h5").text();
  $("#formprivercy").find("input[name='elementname']").val(getElement)
  if (/unlock/.test($(this).attr("class"))) {
      $("input[value='public']").prop("checked", true);
  } else {
      $("input[value='private']").prop("checked", true);
  }

  $("#formprivercy").show()
});
$(document).on("change", "input[name='privercy']", function(){setprivercy();});
function setprivercy(){

  var getprivercy = $(this).val();
  nameDirFile = $("#formprivercy").find("input[name='elementname']").val();
  $.post("/setprivercy", JSON.stringify({
      R: ActuelDir,
      nameDirFile: nameDirFile,
      "privercy": getprivercy
  }), function(jsonn) {
      $("#formprivercy").hide();

      if (jsonn["error"] != 0) alert(jsonn["txt"]);


      var contentReplace;
      if (getprivercy == "public") contentReplace = "iconprivercy fas fa-unlock";
      else contentReplace = "iconprivercy fas fa-lock";

      $(".card").each(function(index, ele) {

          if (jsonn["type"] == "file") {
              if ($(ele).children(".icondir").length == 0 && $(ele).find("h5").text() == nameDirFile) {

                  $(ele).find(".iconprivercy").attr("class", contentReplace);
              }
          } else {
              if ($(ele).children(".icondir").length != 0 && $(ele).find("h5").text() == nameDirFile) {
                  $(ele).find(".iconprivercy").attr("class", contentReplace);

              }
          }

      });


  });

})

$(document).on("change", ".file-input2", function() {
  uploadfile(this)
});

function uploadfile(inputfile) {

  getFiles = $(inputfile).prop("files");

  if (!getFiles || getFiles.length == 0) return;


  if (getFiles.length >= 6) {
      aler("Veuillez sélectionner un maximum de 5 photos");
      return;
  }
  var newform = new FormData();
  for (var i = 0; i < getFiles.length; i++)
      newform.append("myFiles", getFiles[i]);

  newform.append("dir", ActuelDir);

  $("progress").css("display", "block");
  $.ajax({
      url: '/setFiles',
      //headers: {'X-Requested-With': 'XMLHttpRequest'},
      type: 'POST',
      data: newform,
      processData: false,
      cache: false,
      contentType: false,
      xhr: function() {
          var xhrr = $.ajaxSettings.xhr();
          if (xhrr.upload) {
              //in case wont work comment /*.upload.*/
              xhrr.upload.addEventListener('progress', function(e) {
                  if (e.lengthComputable) {
                      $("progress").attr({
                          value: e.loaded,
                          max: e.total
                      });
                  }
              }, false);
          }
          return xhrr;
      },
      dataType: 'json',
      success: function(jsonn) {
          $("progress").css("display", "none");
          addFiles(jsonn["files"], jsonn["path"]);

      }
  });

}


$(document).on("click", ".icondir", function() {
  goTo(this)
})

function goTo(direlment) {

  var getElement = $(direlment).parent().find("h5").text();
  ActuelDir = ActuelDir + "/" + getElement
  getDir()
}


$(document).on("click", ".adddir", function() {
  adddirName()
})

function adddirName() {

  if ($("#creatDir").length != 0) return;
  $(".emptydir").remove();

  newcontent = '<div style="display:none;"class="card" style="width: 18rem;"><i class="fas fa-folder icondir"></i><div class="card-body"><h5 class="card-title"><input type="text" id="namenewdir" placeholder="Dir Name"/> <input type="button" id="creatDir" class="btn btn-primary" value="Submit"/><input type="button" id="creatcancel" class="btn btn-secondary" value="Cancel"/><br><em class="err"></em></h5></div></div>';
  $(newcontent).prependTo(".rootdir").promise().done(function() {
      $(".rootdir .card:eq(0)").show("slow")
  })
}

$(document).on("click", "#creatcancel", function() {$(this).parents(".card").hide(function(){$(this).remove()})});

$(document).on("click", "#creatDir", function() {
  creatDir()
})

function creatDir() {

  var getNameDir = $("#namenewdir").val();

  $(".err").text("");
  fetch('/setDir', {
          method: 'POST',
          body: JSON.stringify({
              funct: "add",
              namedir: getNameDir,
              R: ActuelDir
          })
      })
      .then(response => response.json())
      .then(result => {

          if (result["error"] == 1) {
              $(".err").text(result["txt"]);
              return;
          }
          $("#creatDir").parents(".card").find("h5").html($("#namenewdir").val());
          ActuelDir = ActuelDir + "/" + getNameDir
          getDir()
      });

}


$(document).on("click", ".rename", function() {
  reNameDir(this)
})

function reNameDir(ele) {
  var getActuelName = $(ele).parents(".card").find("h5").text();
  if (getActuelName.lastIndexOf(".") != -1)
      getWithoutExtension = getActuelName.substring(0, getActuelName.lastIndexOf("."));
  else {
      getWithoutExtension = getActuelName
  }
  $(ele).parents(".card").find("h5").html('<input type="text" id="renamedirtxt" data="' + getActuelName + '" value="' + getWithoutExtension + '"placeholder="Dir Name"/> <input type="button" id="renameDir" class="btn btn-primary" value="Submit"/><br><em class="err"></em>')

}
$(document).on("click", "#renameDir", function() {
  exerenameDir()
})

function exerenameDir() {

  var getNameDirFile = $("#renamedirtxt").val();
  var getOLDNameDirFile = $("#renamedirtxt").attr("data");


  $(".err").text("");
  fetch('/setDir', {
          method: 'POST',
          body: JSON.stringify({
              funct: "rename",
              namedir: getNameDirFile,
              olddir: getOLDNameDirFile,
              R: ActuelDir
          })
      })
      .then(response => response.json())
      .then(result => {

          if (result["error"] == 1) {
              $("#renameDir").parent().find(".err").text(result["txt"]);
              return;
          }
          $("#renameDir").parents(".card").find("h5").html(getNameDirFile);

      });

}


$(document).on("click", ".delete", function() {
  deleteDir(this)
})

function deleteDir(ele) {

  var getNameDir = $(ele).parents(".card").find("h5").text();

  $(".err").text("");
  fetch('/setDir', {
          method: 'POST',
          body: JSON.stringify({
              funct: "delete",
              namedir: getNameDir,
              R: ActuelDir
          })
      })
      .then(response => response.json())
      .then(result => {

          if (result["error"] == 1) {
              $(ele).parents(".card").find(".err").text(result["txt"]);
              return;
          }
          $(ele).parents(".card").hide(function() {
              $(ele).parents(".card").remove();
          })

      });
}

$(document).on("click", ".copy,.move", function() {
  callTocopymoveDir(this)
})

function callTocopymoveDir(ele) {
  if ($("#paste").length != 0) {
      alert("You have to Cancel first copy/move function");
  }
  var contentCopy = '<div id="paste"class="btn-group" role="group" aria-label="Basic example"><button type="button" class="cancel btn btn-secondary">Cancel</button><button type="button" class="paste btn btn-secondary">Paste</button></div>';

  var getNameDir = $(ele).parents(".card").find("h5").text();
  from = ActuelDir + "/" + getNameDir;

  var functionIs = "";

  if (/copy/.test($(ele).attr("class"))) {
      functionIs = "copy"
  } else {
      functionIs = "move";
  }

  $(contentCopy).css({
      "position": "fixed",
      "right": "20px",
      "bottom": "100px"
  }).on("click", function(e) {


      e = e || window.event;
      var targ = e.target || e.srcElement;
      if (/cancel/.test(targ.className)) {
          $("#paste").remove();
          return
      }
      if (/paste/.test(targ.className)) {

          copymoveDir(functionIs, from, ele)

      }

  }).appendTo("body");
}

function copymoveDir(functionIs, from, ele) {



  $(".err").text("");
  fetch('/setDir', {
          method: 'POST',
          body: JSON.stringify({
              funct: functionIs,
              fromnamedir: from,
              R: ActuelDir
          })
      })
      .then(response => response.json())
      .then(result => {
          $("#paste").remove();
          if (result["error"] == 1) {
              alert(result["txt"]);
              return;
          }


          if (result["type"] == "dir") {
              newcontent = '<div class="card" style="width: 18rem;"><i class="iconprivercy fas fa-lock"></i><i class="fas fa-folder icondir"></i><div class="card-body"><h5 class="card-title">' + result["name"] + '</h5></div>' + getOptions + '</div>';
              if (functionIs == "move") $(ele).parents(".card").hide(function() {
                  $(ele).parents(".card").remove();
              })

          } else {
              if (functionIs == "move") $(ele).parents(".card").hide(function() {
                  $(ele).parents(".card").remove();
              })
              newcontent = '<div class="card" style="width: 18rem;"><i class="iconprivercy fas fa-lock"></i>' + formatfile(result.type, result["name"], result.path) + '<div class="card-body"><h5 class="card-title">' + result["name"] + '</h5></div>' + getOptions + '</div>';
          }
          $(".rootdir").prepend(newcontent)



      });
}

$(document).on("click", ".download", function() {
  downloadDir(this)
})

function downloadDir(ele) {

  var getNameDir = $(ele).parents(".card").find("h5").text();


  location.href = "/download?path=" + ActuelDir + "&dir=" + getNameDir;



}

function getDir() {
  $(".rootdir").html("")


  $(".backward").off(); //init handle


  fetch('/getDir', {
          method: 'POST',
          body: JSON.stringify({
              R: ActuelDir
          })
      })
      .then(response => response.json())
      .then(result => {

          $(".emplacement em").text(result["repertoir"].path);
          if (result["repertoir"].backward) {
              $(".backward").css("color", "black");

              $(".backward").on("click", function(event) {

                  event.stopPropagation()
                  ActuelDir = result["repertoir"].path.substring(result["repertoir"].path.lastIndexOf("/"), 0)

                  getDir()
              });

          } else $(".backward").css("color", "#d5d5d5");

          ActuelDir = result["repertoir"].path;

          if (result["repertoir"] == false) {
              /*--------------------------------------------------*/
            }


          getDirs = result["repertoir"]["dirs"];
          var newcontent;
          var lockunlock
          if (result["repertoir"]["dirs"].length == 0 && result["repertoir"]["files"].length == 0) {
              return $(".rootdir").prepend("<p class='emptydir'>This directory is empty</p>")
          }
          for (var i = 0; i < getDirs.length; i++) {

              if (getDirs[i]["privercy"] == "public") lockunlock = "unlock";
              else lockunlock = "lock";

              newcontent = '<div class="card" style="width: 18rem;"><i class="iconprivercy fas fa-' + lockunlock + '"></i><i class="fas fa-folder icondir"></i><div class="card-body"><h5 class="card-title">' + getDirs[i].name + '</h5></div>' + getOptions + '</div>';
              $(".rootdir").prepend(newcontent)
          }

          getFiles = result["repertoir"]["files"];
          addFiles(getFiles, result["repertoir"].path);

      });

}

var formatfile = function(format, name, path) {
  if (format == "png" || format == "jpg" || format == "jpeg" || format == "gif")
      return "<img src='/media/" + path + "/" + name + "' alt='" + name + "'>";
  else
      return '<i class="fas fa-file iconfile"></i>';
};

function addFiles(getFiles, path) {

  for (var i = 0; i < getFiles.length; i++) {

      if (getFiles[i]["privercy"] == "public") lockunlock = "unlock";
      else lockunlock = "lock";

      newcontent = '<div class="card" style="width: 18rem;"><i class="iconprivercy fas fa-' + lockunlock + '"></i>' + formatfile(getFiles[i].type, getFiles[i].name, path) + '<div class="card-body"><h5 class="card-title">' + getFiles[i].name + '</h5></div>' + getOptions + '</div>';
      $(".rootdir").prepend(newcontent)
  }

}


const getOptions = '<div class="btn-group" role="group" aria-label="Basic example"> <button type="button" class="delete btn btn-secondary" title="delete"><i class="iconcard fas fa-trash"></i></button><button type="button"  title="download" class="download btn btn-secondary"><i class="iconcard fas fa-download"></i></button> <button type="button" title="move" class="move btn btn-secondary"><i class="iconcard fas fa-expand-alt"></i></button> <button type="button" title="copy" class="copy btn btn-secondary"><i class="iconcard  fas fa-copy"></i></button> <button type="button" class="rename btn btn-secondary" title="rename"><i class="iconcard  fas fa-pen"></i></button> </div>'


$(document).on("click",".navbar-toggler",function(){$("#navbarSupportedContent").toggle()})
