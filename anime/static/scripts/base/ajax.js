/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * AJAX module
 *
 */

//################# Ajax worker

define(['base/cookies', 'base/request_processor'],
    function(cookies, RequestProcessor) {

    function AjaxClass(){

        var defaultProcessor = new RequestProcessor({})
        this.url = '/ajax/'

        //################# Вызов аяксового обьекта.
        this.loadXMLDoc = function(url, qry, processor){

            if(!isHash(processor) || !isFunction(processor.process))
                processor = defaultProcessor

            var xmlHttp = null
            if(window.XMLHttpRequest){
                try{
                    xmlHttp = new XMLHttpRequest()
                }catch(e){}
            }else if(window.ActiveXObject){
                try{
                    xmlHttp = new ActiveXObject('Msxml2.XMLHTTP')
                }catch(e){
                    try{
                        xmlHttp = new ActiveXObject('Microsoft.XMLHTTP')
                    }catch(e){}
                }
            }

            processor.setRequest()
            var data = makeRequest(url, qry)

            if(data.request){
                if (xmlHttp){
                    xmlHttp.open("POST", this.url + url + '/', true)
                    xmlHttp.onreadystatechange = processor.process
                    xmlHttp.setRequestHeader("Content-type",
                            "multipart/form-data; boundary=" + data.boundary)
                    xmlHttp.send(data.request)
                }
            }
        }

        var makeRequest = function(url, qry){
            var request = ''

            if(!(/^http:.*/.test(url) || /^https:.*/.test(url)))
                qry['csrfmiddlewaretoken'] = cookies.get('csrftoken')

            var boundary = '-----------' + parseInt(Math.random()*1000000000000)

            var makePostData = function(name, value){
                var crlf = '\r\n'
                var s = '--' + boundary + crlf
                s += 'Content-Disposition: form-data; name="' + name + '"'
                // isFile
                if(value !== null && typeof value == "object" &&
                        'lastModifiedDate' in value && 'name' in value){
                    s += '; filename="' + value.name + '"' + crlf
                    s += 'Content-Type: application/octet-stream' + crlf
                    var reader = new FileReader()
                    reader.readAsBinaryString(value)
                    s += crlf + reader.result + crlf
                }else{
                    s += crlf + crlf + (!isString(value) ? jsonToString(value) : value) + crlf
                }
                return s
            }

            for(var item in qry){
                if(!item || !qry[item])
                    continue
                if(isArray(qry[item]))
                    request += map(function(itm) {
                        return makePostData(item, itm) }, qry[item]).join('')
                else
                    request += makePostData(item, qry[item])
            }
            request += '--' + boundary + '--'

            return {'request': request, 'boundary': boundary}
        }
    }

    var ajax = new AjaxClass()
    AjaxClass.prototype.load = ajax.loadXMLDoc

    return ajax
})