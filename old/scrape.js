

(async function () {
    const mql = require('@microlink/mql')
    
    
     const {status, data } =  await mql('https://www.verivox.de/stromvergleich/vergleich?bonus=OnlyCompliant&partnerid=1&persons=on&plocation=1757&plz=53757&product=electricity&source=1&usage=1500&profile=H0&q=WzYsMCwwLDEsMCwwLDEsMiwyMCwwLDEsNzE4NTkyLCI1MDgyMyIsMSwyNDAsMjQwLDE1MDAsMCwwLDAsOTk5LC0xLC0xLC0xLDAsMCwiVG90YWxDb3N0cyIsIkFzY2VuZGluZyIsIk5vbmUiLDc1OTQ1LCJOb1NwZWNpYWxWaWV3IiwwXQ%3D%3D', {
        waitFor: 3000,
        data: {
          posts: {
            selectorAll: 'div',
            attr: 'text'
          },
        },
        
      })
    
      console.log(status, data)
    }());
