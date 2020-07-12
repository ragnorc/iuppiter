import faunadb from "https://jspm.dev/faunadb"
import moment from "https://jspm.dev/moment";

const q = faunadb.query

var client = new faunadb.Client({ secret: 'fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO', fetch: fetch })



const get_power_futures = async (product, type) => {
  let url = `https://wrapapi.com/use/ragnorc/eex/futures/latest?wrapAPIKey=Vw52prEVYvxTYP7JN9MpNCIDVOKvf2iI&product=%22%2FE.DE${type.charAt(0).toUpperCase()}${product.charAt(0).toUpperCase()}%22&expirationDate=${encodeURI(new Date().toJSON().slice(0,10).replace(/-/g,'/'))}&onDate=null`
  console.log(url)
  let response = await fetch(url)

  let data = (await response.json()).data.output.reduce((result, item)=> {
    if (item.ontradeprice || item.close) {
    let tradeTime = moment.utc(item.tradedatetimegmt, "M/D/YYYY h:mm:ss a").toISOString()
    result.push({
      original: {
        ...item
      },
      tradeTime: tradeTime? q.Time(tradeTime) : null,
      tradePrice: item.ontradeprice,
      closePrice: item.close,
      type,
      product,
      [product]: moment(item["gv.displaydate"], "M/D/YYYY")[product]()
    })
  }
  return result
  },[])

  
  client.query(
    q.Map(
      data,
      q.Lambda(
        'item',
        q.Create(
          q.Collection('PowerFuture'),
          { data: q.Var("item") },
        )
      ),
    )
  )
  .then((ret) => console.log(ret))
}


let products =  ["year","quarter", "month"]

for (let product of products) {
  get_power_futures(product, "base")
  get_power_futures(product, "peak")
}
