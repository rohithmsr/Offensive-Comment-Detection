


var commentIndex = 0;



$(document).on('DOMSubtreeModified', async (event) => {

    var arr = $(event.currentTarget).find('yt-formatted-string#content-text').not('.verified');



    if (arr.length > 0) {


        if ($(arr[0]).attr('comment-id') == null) {


            await $(arr[0]).attr('comment-id', commentIndex++ );
            await $(arr[0]).addClass( ''+commentIndex );
            // console.log("----------");




            await new Promise( async (resolve, reject) => {
        
                try {
                

                    // console.log( $('.'+commentIndex).text() );


                    $.ajax({
                        headers: {        
                            "Access-Control-Allow-Origin" : "*",
                            "Access-Control-Allow-Methods":  "GET,HEAD,OPTIONS,POST,PUT",
                            "Access-Control-Allow-Headers":  "Origin, X-Requested-With, Content-Type, Accept",
                            "Access-Control-Allow-Private-Network": "true",
                        },
                        type: 'POST',
                        cache: false,
                        xhrFields: { withCredentials: true },
                        url: "http://127.0.0.1:8000/predict",
                        data: JSON.stringify({
                            "comment_id": commentIndex,
                            "text": $('.'+commentIndex).text()
                        }),
                        dataType : "json",
                        contentType: "application/json; charset=utf-8",
                        success: function(resultData) {

                            console.log("----------");
                            console.log( resultData.comment_id );
                            console.log( $('.'+resultData.comment_id).text() );
                            console.log( resultData.offensive );

                            if (resultData.offensive == 1) {
                                $('.'+resultData.comment_id).html('<span style="color: red;">THIS COMMENT HAS OFFENSIVE CONTENT. SO IT IS BLOCKED BY ACD EXTENSION</span>');
                            }

                
                            console.log("----------");
                        },
                    });





                


            } catch (error) {
                console.error(error);
            }
                



                
                resolve("ok");
            })
            .then((data) => {
                
                $('.'+commentIndex).html();
    
                $('.'+commentIndex).addClass( 'verified' );
            })


                
    
            
            
        
    
            // console.log("----------");

        }



    }




});






