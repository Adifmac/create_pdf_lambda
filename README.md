# create_pdf_lambda
aws lambda function for creating PDF from list of photos

Example event data:
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

