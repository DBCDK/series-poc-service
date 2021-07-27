use( "Log" );
use( "Print" );
use( "XmlUtil" );
use( "MarcXchange" );


//required function for jspipetool, will be executed before all records are processed
function begin() {
    printn( "[" );

}

//default work function for jspipetool
function work( record ) {

    var xml = XmlUtil.fromString( record );
    var marcRecord = MarcXchange.marcXchangeToMarcRecord( xml );

    var outputJson = {};

    outputJson[ "workId" ] = "870970-basis" + marcRecord.getValue( "001", "a" );

//series title
    var f530i = marcRecord.getValue( "530", "i" );
    if ( "" !== f530i ) {
        outputJson[ "seriesTitle" ] = f530i;
    }
//series description
    var f530b = marcRecord.getValue( "530", "b" );
    if ( "" !== f530b ) {
        outputJson[ "seriesDescription" ] = f530b;
    }
//series alternative title
    var alternativeTitles = [];
    marcRecord.field( "530" ).eachSubField( "x", function( field, subfield ) {
        alternativeTitles.push( subfield.value );
    } );
    if ( 0 !== alternativeTitles.length ) {
        outputJson[ "seriesAlternativeTitle" ] = alternativeTitles;
    }
// number in series
    var numberInSeries = [];
    marcRecord.field( "530" ).eachSubField( "d", function( field, subfield ) {
        numberInSeries.push( subfield.value );
    } );
    if ( 0 !== numberInSeries.length ) {
        outputJson[ "numberInSeries" ] = numberInSeries;
    }
//number in universe
    var f530c = marcRecord.getValue( "530", "c" );
    if ( "" !== f530c ) {
        outputJson[ "numberInUniverse" ] = f530c;
    }


    printn( JSON.stringify( outputJson ) + "," );

}

//required function for jspipetool, will be executed after all records are processed
function end() {
    printn( "]" );

}

