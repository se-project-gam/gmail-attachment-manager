var config = {
  'client_id': '705976105857-oj6a49bi1rfquusot5mbjpvo1daraerk.apps.googleusercontent.com',
  'scope': 'https://www.googleapis.com/auth/gmail.readonly'
};

function checkAuth() {
  gapi.auth.authorize(config, handleAuthResult);
}

function handleAuthResult(authResult) {
  var authorizeButton = document.getElementById('authorize-button');
  if (authResult && !authResult.error) {
    makeApiCall();
  }
}

function makeApiCall() {
  gapi.client.load('gmail', 'v1', function() {
    var messages = gapi.client.gmail.users.messages.list({
      'userId': 'me',

      'pageToken' : '05572196950464279653'
    });
    messages.execute(function(resp) {
      var message = document.createElement('div');
      for (i in resp.messages){
        var msg_id = resp.messages[i].id;

        var msg = gapi.client.gmail.users.messages.get({
          'userId': 'me',
          'id': msg_id
        });
        msg.execute(function(rmsg){
          var lfrom = "";
          var lto = "";
          var lsubject = "";
          console.log(rmsg);
          for (j in rmsg.payload.headers){
            var item = rmsg.payload.headers[j];
            if (item.name == 'From') lfrom = item.value;
            if (item.name == 'To') lto = item.value;
            if (item.name == 'Subject') lsubject = item.value;
          }
          var emsg_id = document.createElement('h2');
          var efrom = document.createElement('h4');
          var eto = document.createElement('h4');
          var esubject = document.createElement('h4');

          var tmsg_id = document.createTextNode('Msg id: ' + msg_id);
          var tfrom = document.createTextNode('From: ' + lfrom);
          var tto = document.createTextNode('To: ' + lto);
          var tsubject = document.createTextNode('Subject: ' + lsubject);

          emsg_id.appendChild(tmsg_id);
                efrom.appendChild(tfrom);
          eto.appendChild(tto);
          esubject.appendChild(tsubject);

          message.appendChild(emsg_id);
          message.appendChild(efrom);
          message.appendChild(eto);
          message.appendChild(esubject);

          for (j in rmsg.payload.parts){
            var item = rmsg.payload.parts[j];
            var lfilename = '';
            var lattachmentId = '';
            var lsize = '';
            if (item.filename){
              lfilename = item.filename;
              lattachmentId = item.body.attachmentId;
              lsize = item.body.size;

              var efilename = document.createElement('p');
              var eattachmentId = document.createElement('p');
              var esize = document.createElement('p');

              var tfilename = document.createTextNode('File Name: ' + lfilename);
              var tattachmentId = document.createTextNode('Attachment ID: ' + lattachmentId);
              var tsize = document.createTextNode('Size: ' + lsize);

              efilename.appendChild(tfilename);
              eattachmentId.appendChild(tattachmentId);
              esize.appendChild(tsize);

              message.appendChild(efilename);
              message.appendChild(eattachmentId);
              message.appendChild(esize);
            }
          }
        });
      }
      document.getElementById('content').appendChild(message);
    });
  });
}