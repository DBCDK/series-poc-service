use( "Log" );
use( "Print" );
use ( "XmlUtil" );
use ( "MarcXchange" );


//required function for jspipetool, will be executed before all records are processed
function begin() {
    printn( "[" );

}

//default work function for jspipetool
function work( record  ) {

var xml = XmlUtil.fromString( record );
var marcRecord = MarcXchange.marcXchangeToMarcRecord( xml );

var outputJson = {};

var workId = "870970-basis" + marcRecord.getValue( "001", "a" );

outputJson[ "workId" ] = workId;


printn( JSON.stringify( outputJson ) + "," );

}

//required function for jspipetool, will be executed after all records are processed
function end() {
    printn( "]" );

}

