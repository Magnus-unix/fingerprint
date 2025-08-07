function getCanvasFingerprint(): { winding: boolean, geometry: string, text: string } {
    let winding = false;
    let geometry: string;
    let text: string;

    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const context = canvas.getContext('2d');

    if (!context || !canvas.toDataURL) {
        geometry = text = 'unsupported';
    } else {
        winding = doesSupportWinding(context);

        const [geo, txt] = renderImages(canvas, context);
        geometry = geo;
        text = txt;
    }

    return { winding, geometry, text };
}

function doesSupportWinding(context: CanvasRenderingContext2D): boolean {
    context.rect(0, 0, 10, 10);
    context.rect(2, 2, 6, 6);
    return !context.isPointInPath(5, 5, 'evenodd');
}

function renderImages(canvas: HTMLCanvasElement, context: CanvasRenderingContext2D): [string, string] {
    renderTextImage(canvas, context);
    const textImage1 = canvas.toDataURL();
    const textImage2 = canvas.toDataURL();

    if (textImage1 !== textImage2) {
        return ['unstable', 'unstable'];
    }

    renderGeometryImage(canvas, context);
    const geometryImage = canvas.toDataURL();

    return [geometryImage, textImage1];
}

function renderTextImage(canvas: HTMLCanvasElement, context: CanvasRenderingContext2D) {
    canvas.width = 240;
    canvas.height = 60;

    context.textBaseline = 'alphabetic';
    context.fillStyle = '#f60';
    context.fillRect(100, 1, 62, 20);

    context.fillStyle = '#069';
    context.font = '11pt "Times New Roman"';
    const printedText = `Cwm fjordbank gly ${String.fromCharCode(55357, 56835) /* 😃 */}`;
    context.fillText(printedText, 2, 15);

    context.fillStyle = 'rgba(102, 204, 0, 0.2)';
    context.font = '18pt Arial';
    context.fillText(printedText, 4, 45);
}

function renderGeometryImage(canvas: HTMLCanvasElement, context: CanvasRenderingContext2D) {
    canvas.width = 122;
    canvas.height = 110;

    context.globalCompositeOperation = 'multiply';
    const circles: [string, number, number][] = [
        ['#f2f', 40, 40],
        ['#2ff', 80, 40],
        ['#ff2', 60, 80],
    ];

    for (const [color, x, y] of circles) {
        context.fillStyle = color;
        context.beginPath();
        context.arc(x, y, 40, 0, Math.PI * 2, true);
        context.closePath();
        context.fill();
    }

    context.fillStyle = '#f9c';
    context.arc(60, 60, 60, 0, Math.PI * 2, true);
    context.arc(60, 60, 20, 0, Math.PI * 2, true);
    context.fill('evenodd');
}

