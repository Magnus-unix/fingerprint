function getFontsFingerprint(): Promise<string[]> {
  return new Promise((resolve) => {
      const testString = 'mmMwWLliI0O&1'
      const textSize = '48px'
      const baseFonts = ['monospace', 'sans-serif', 'serif']
      const fontList = [
          'sans-serif-thin', 'ARNO PRO', 'Agency FB', 'Arabic Typesetting',
          'Arial Unicode MS', 'AvantGarde Bk BT', 'BankGothic Md BT', 'Batang',
          'Bitstream Vera Sans Mono', 'Calibri', 'Century', 'Century Gothic',
          'Clarendon', 'EUROSTILE', 'Franklin Gothic', 'Futura Bk BT', 'Futura Md BT',
          'GOTHAM', 'Gill Sans', 'HELV', 'Haettenschweiler', 'Helvetica Neue',
          'Humanst521 BT', 'Leelawadee', 'Letter Gothic', 'Levenim MT', 'Lucida Bright',
          'Lucida Sans', 'Menlo', 'MS Mincho', 'MS Outlook', 'MS Reference Specialty',
          'MS UI Gothic', 'MT Extra', 'MYRIAD PRO', 'Marlett', 'Meiryo UI',
          'Microsoft Uighur', 'Minion Pro', 'Monotype Corsiva', 'PMingLiU',
          'Pristina', 'SCRIPTINA', 'Segoe UI Light', 'Serifa', 'SimHei',
          'Small Fonts', 'Staccato222 BT', 'TRAJAN PRO', 'Univers CE 55 Medium',
          'Vrinda', 'ZWAdobeF'
      ]

      const defaultWidth: Record<string, number> = {}
      const defaultHeight: Record<string, number> = {}

      const spansContainer = document.createElement('div')
      spansContainer.style.visibility = 'hidden'
      spansContainer.style.position = 'absolute'
      spansContainer.style.top = '0'
      spansContainer.style.left = '0'
      spansContainer.style.fontSize = textSize

      const createSpan = (fontFamily: string) => {
          const span = document.createElement('span')
          span.style.fontFamily = fontFamily
          span.textContent = testString
          spansContainer.appendChild(span)
          return span
      }

      const createSpanWithFallback = (font: string, baseFont: string) => {
          return createSpan(`'${font}',${baseFont}`)
      }

      // Create spans for base fonts and record their default dimensions
      const baseFontSpans = baseFonts.map(createSpan)
      baseFonts.forEach((font, i) => {
          defaultWidth[font] = baseFontSpans[i].offsetWidth
          defaultHeight[font] = baseFontSpans[i].offsetHeight
      })

      // Create spans for all test fonts against each base font
      const fontSpans: Record<string, HTMLElement[]> = {}
      for (const font of fontList) {
          fontSpans[font] = baseFonts.map(base => createSpanWithFallback(font, base))
      }

      document.body.appendChild(spansContainer)

      const availableFonts = fontList.filter(font => {
          return fontSpans[font].some((span, i) =>
              span.offsetWidth !== defaultWidth[baseFonts[i]] ||
              span.offsetHeight !== defaultHeight[baseFonts[i]]
          )
      })

      document.body.removeChild(spansContainer)
      resolve(availableFonts)
  })
}
