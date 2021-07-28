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
    var output = "";

    var addField534Data = function( outputJson, marcRecord ) {
        //universe title
        var f534i = marcRecord.getValue( "534", "i" );
        if ( "" !== f534i ) {
            outputJson[ "universeTitle" ] = f534i;
        }

//universe description
        var f534b = marcRecord.getValue( "534", "b" );
        if ( "" !== f534b ) {
            outputJson[ "universeDescription" ] = f534b;
        }

//universe alternative title
        var f534x = marcRecord.getValue( "534", "x" );
        if ( "" !== f534x ) {
            outputJson[ "universeAlternativeTitle" ] = f534x;
        }
    }


    if ( marcRecord.existField( "530" ) ) {


        marcRecord.eachField( "530", function( field ) {

            var outputJson = {};

            outputJson[ "workId" ] = "870970-basis:" + marcRecord.getValue( "001", "a" );

//series title
            var f530i = field.getValue( "i" );
            if ( "" !== f530i ) {
                outputJson[ "seriesTitle" ] = f530i;
            }
//series description
            var f530b = field.getValue( "b" );
            if ( "" !== f530b ) {
                outputJson[ "seriesDescription" ] = f530b;
            }
//series alternative title
            var alternativeTitles = [];
            field.eachSubField( "x", function( field, subfield ) {
                alternativeTitles.push( subfield.value );
            } );
            if ( 0 !== alternativeTitles.length ) {
                outputJson[ "seriesAlternativeTitle" ] = alternativeTitles;
            }
// number in series
            var numberInSeries = [];
            field.eachSubField( "d", function( field, subfield ) {
                numberInSeries.push( subfield.value );
            } );
            if ( 0 !== numberInSeries.length ) {
                outputJson[ "numberInSeries" ] = numberInSeries;
            }
//number in universe
            var f530c = field.getValue( "c" );
            if ( "" !== f530c ) {
                outputJson[ "numberInUniverse" ] = f530c;
            }

//read first
            var f530e = field.getValue( "e" );
            if ( "" !== f530e ) {
                outputJson[ "readFirst" ] = true;
            }

//can be read independently
            var f530g = field.getValue( "g" );
            if ( "" !== f530g ) {
                outputJson[ "canBeReadIndependently" ] = true;
            }

            addField534Data( outputJson, marcRecord );

            output += JSON.stringify( outputJson ) + ",";

        } )
    } //end field 530 exists
    else {
        var outputJson = {};
        outputJson[ "workId" ] = "870970-basis:" + marcRecord.getValue( "001", "a" );
        addField534Data( outputJson, marcRecord );
        output += JSON.stringify( outputJson ) + ",";
    }


    printn( output );

}

//required function for jspipetool, will be executed after all records are processed
function end() {
    printn( "]" );

}


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
    var output = "";

    var addField534Data = function( outputJson, marcRecord ) {
        //universe title
        var f534i = marcRecord.getValue( "534", "i" );
        if ( "" !== f534i ) {
            outputJson[ "universeTitle" ] = f534i;
        }

//universe description
        var f534b = marcRecord.getValue( "534", "b" );
        if ( "" !== f534b ) {
            outputJson[ "universeDescription" ] = f534b;
        }

//universe alternative title
        var f534x = marcRecord.getValue( "534", "x" );
        if ( "" !== f534x ) {
            outputJson[ "universeAlternativeTitle" ] = f534x;
        }
    }


    if ( marcRecord.existField( "530" ) ) {


        marcRecord.eachField( "530", function( field ) {

            var outputJson = {};

            outputJson[ "workId" ] = "870970-basis:" + marcRecord.getValue( "001", "a" );

//series title
            var f530i = field.getValue( "i" );
            if ( "" !== f530i ) {
                outputJson[ "seriesTitle" ] = f530i;
            }
//series description
            var f530b = field.getValue( "b" );
            if ( "" !== f530b ) {
                outputJson[ "seriesDescription" ] = f530b;
            }
//series alternative title
            var alternativeTitles = [];
            field.eachSubField( "x", function( field, subfield ) {
                alternativeTitles.push( subfield.value );
            } );
            if ( 0 !== alternativeTitles.length ) {
                outputJson[ "seriesAlternativeTitle" ] = alternativeTitles;
            }
// number in series
            var numberInSeries = [];
            field.eachSubField( "d", function( field, subfield ) {
                numberInSeries.push( subfield.value );
            } );
            if ( 0 !== numberInSeries.length ) {
                outputJson[ "numberInSeries" ] = numberInSeries;
            }
//number in universe
            var f530c = field.getValue( "c" );
            if ( "" !== f530c ) {
                outputJson[ "numberInUniverse" ] = f530c;
            }

//read first
            var f530e = field.getValue( "e" );
            if ( "" !== f530e ) {
                outputJson[ "readFirst" ] = true;
            }

//can be read independently
            var f530g = field.getValue( "g" );
            if ( "" !== f530g ) {
                outputJson[ "canBeReadIndependently" ] = true;
            }

            addField534Data( outputJson, marcRecord );

            output += JSON.stringify( outputJson ) + ",";

        } )
    } //end field 530 exists
    else {
        var outputJson = {};
        outputJson[ "workId" ] = "870970-basis:" + marcRecord.getValue( "001", "a" );
        addField534Data( outputJson, marcRecord );
        output += JSON.stringify( outputJson ) + ",";
    }


    printn( output );

}

//required function for jspipetool, will be executed after all records are processed
function end() {
    printn( "]" );

}



