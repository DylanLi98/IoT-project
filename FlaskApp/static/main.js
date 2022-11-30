window.isLightOn = false;

function lightControl(valName)
{
	let val = document.getElementsByName(valName);
	if (window.isLightOn == false){
		val[0].style.backgroundColor = "yellow";
		window.isLightOn = true
	} else {
		val[0].style.backgroundColor = "blue";
		window.isLightOn = false
	}
	
}