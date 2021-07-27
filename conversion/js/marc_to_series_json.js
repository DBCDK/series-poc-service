use( "Log" );
use( "Print" );
use ("XmlUtil");
use ("MarcXchange");


var argv = System.arguments;

function begin() {
    printn("[");

}


function work( record  ) {

var xml = XmlUtil.fromString( record );
var marcRecord = MarcXchange.marcXchangeToMarcRecord( xml );

var outputJson = {};

var workId = "870970-basis" + marcRecord.getValue("001", "a");

outputJson["workId"] = workId;


printn( JSON.stringify(outputJson ) + "," );

}



function end() {
    printn("]");


}

