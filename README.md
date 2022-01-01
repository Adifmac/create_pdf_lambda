# create_pdf_lambda
aws lambda function for creating PDF from list of photos.
The function will constract a Html page and convert it to PDF using [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html).

### Pages
- Cover page with logo or name, and contact details as provided.
- Photos pages, each page with a grid of photos according to param `pics_in_page`.
- Each photos page will have a Footer with copy right notice and a link to the website.

### Parameters:

`name` :String -Required

`email` :String -Optional

`phone` :String -Optional

`logo` :String -Optional

`pics_in_page` :Int -Required

`site_url` :String -Required

`photos` :Array of Photo-objects

  photo-object: 
  
   `url` :String -Required
    
   `width` :Int -Required
    
   `height` :Int -Required


### Example event data:
```
{
  "data": {
      "name": "USER-NAME-REQUIRED",
      "email": "USER-EMAIL",
      "phone": "USER-PHONE",
      "logo": "LOGO-IMG",
      "pics_in_page": 4,
      "site_url": "USER-WEBSITE-URL-REQUIRED",
      "photos": [
          {
            "url": "IMG-0-URL",
            "width": 1500,
            "height": 1000
          },
          {
            "url": "IMG-1-URL",
            "width": 857,
            "height": 1200
          }
      ]
  }
}
```

Requires creating a `wkhtmltopdf` lambda layer - instructions: https://bradleyschoeneweis.com/converting-html-to-a-pdf-using-python-aws-lambda-and-wkhtmltopdf

