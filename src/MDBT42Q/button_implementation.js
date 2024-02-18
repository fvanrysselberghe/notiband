function constructMessage() {
  message = new Uint8Array(17);
    message[0] = 205;
    message[1] = 0;
    message[2] = 14;
    message[3] = 18;
    message[4] = 1;
    message[5] = 18;
    message[6] = 0;
    message[7] = 9;
    message[8] = 1;
    message[9] = 0;
    message[10] = 0;
    message[11] = 80;
    message[12] = 97;
    message[13] = 115;
    message[14] = 32;
    message[15] = 111;
    message[16] = 112;
  
  return message;
}

function flag()
{
  console.log("Button press captured");
  
  if (busy) {
    return;
  }
  
  busy = true;
  var gatt; //Global access for our disconnect
  
  NRF.connect('C0:00:00:00:0E:A7')
  .then(function(connection) {
    console.log("Connected to wearable");
    
    gatt = connection; //Store the connection for later
    
    return gatt.getPrimaryService(
        "6e400001-b5a3-f393-e0a9-e50e24dcca9d");
  }).then(function(service) {
    return service.getCharacteristic(
        "6e400002-b5a3-f393-e0a9-e50e24dcca9d");
  }).then(function(characteristic) {
    // Get "Pas Op" message
    var message = constructMessage();
 
    console.log(message); 
    
    return characteristic.writeValue(message);
  }).then(function() {
    if (gatt) {
        gatt.disconnect();
    }
    console.log("Done!");
    busy = false;
  }).catch(function(e) {
    console.log("ERROR",e);
    busy = false;
  });
}

var busy = false;

pinMode(D26, 'input_pullup');
pinMode(D20, 'input_pullup');

setWatch(flag, D26, {repeat:true, debounce: 25, edge: 'rising'});
setWatch(flag, D20, {repeat:true, debounce: 25, edge: 'rising'});


NRF.setServices({}, { uart : false });
NRF.setAdvertising({}, {showName:false, connectable:false, discoverable:false});