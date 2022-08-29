var ci = app.activeDocument.countItems
var plist = "ItemNumber\tXpos\tYpos\timage\n"

var tp = Folder.desktop + "/CountItem.txt";
for (var i = 0; i < ci.length; i++){
    var pos = ci[i].position.toString().split(",")
    var group = ci[i].parent.toString()
    plist += (i+1) + "\t" + pos[0] +"\t" + pos[1] + "\t" + group + "\n"
};

writeText(tp, plist)

/**
* Write a text file
*  the file path
*  the text
*
*/
function writeText(p,s){
    var file = new File(p.toString());
    file.encoding = 'UTF-8';
    file.open('w');
    file.write(s);
    file.close();
}
