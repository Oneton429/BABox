function exportImage() {
	document.querySelector(".export-btn").disabled = true;
	setTimeout(() => {
		htmlToImage.toPng(document.getElementById('main'))
			.then(imgUrl => {
				const link = document.createElement("a");
				link.download = "box.png";
				link.href = imgUrl; link.click();
			})
			.catch(err => {console.error(err)});
		document.querySelector(".export-btn").disabled = false;
	}, 100);
}
addEventListener("load", () => {
	document.querySelector(".export-btn").disabled = false;
});