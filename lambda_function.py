from datetime import datetime, date
import time
import json
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
import pdfkit
from string import Template

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# set up const
destination_bucket = 'BUCKET-NAME'
dry_run = False

# Get the s3 client
s3_client = boto3.client('s3')
s3 = boto3.resource('s3')


@dataclass
class InitObj:
    photos: str
    name: str
    email: str
    phone: str
    logo: str
    pics_in_page: int
    site_url: str


class PdfComposer:
    def release_id(self):
        return datetime.now().strftime('%Y%m%d-%H%M%S')

    def get_photo(self, photo_obj, tpl):
        url = photo_obj['url']
        width = int(photo_obj['width'])
        height = int(photo_obj['height'])
        out_str = '<img src="' + url + '" style="height: '
        if width > height:
            orientation = 'landscape'
        else:
            orientation = 'portrait'
        if tpl == 1:
            if orientation == 'landscape':
                out_str = out_str + '700'
            else:
                out_str = out_str + '650'
        elif tpl == 2:
            if orientation == 'landscape':
                out_str = out_str + '400'
            else:
                out_str = out_str + '500'
        elif tpl == 4:
            if orientation == 'landscape':
                out_str = out_str + '280'
            else:
                out_str = out_str + '380'
        out_str = out_str + 'px; object-fit:contain;">'

        return out_str

    def get_doc_header(self, title_str):
        header_str = '''<!DOCTYPE html>
        <html>
          <head>
            <title>$title</title>
            <style type="text/css" media="screen">
                html { height: 0; }
                body {
                    font-family: 'Open Sans', sans-serif;
                    font-weight: 300;
                }
                .container { 
                    page-break-before: always;
                    page-break-inside: avoid;
                    height: 870px;
                }
                .col_top {
                    height:870px; 
                    display: grid; 
                    text-align:center;
                    position:relative;
                    page-break-inside: avoid;
                }
                .col {
                    color: #666666; 
                    font-size: 10px; 
                    letter-spacing: 0.5px;
                }
                .wrapper {
                    margin: auto; 
                    display:inline-block; 
                    vertical-align:center;
                }
                .center {
                    margin: auto;
                    vertical-align:center;
                    padding:10px;
                    font-size:10px;
                }
                .cantered {
                    position: absolute; 
                    top: 50%; 
                    left: 50%; 
                    transform: translate(-50%, -50%);
                    -webkit-transform: translate(-50%, -50%); -moz-transform: translate(-50%, -50%);
                    -o-transform: translate(-50%, -50%); -ms-transform: translate(-50%, -50%);
                    padding:30px;
                }
                .liner_left {
                    display:inline-block;
                    padding:5px 10px;
                    color: #666666; 
                }
                .liner_right {
                    display:inline-block;
                    border-left:1px solid #ccc;
                    padding:5px 10px;
                    color: #666666; 
                }
                td { vertical-align: middle; }
                a { color: #666666; text-decoration: none; font-weight: bold;}
            </style>
          </head>
        <body>'''
        return Template(header_str).substitute(title=title_str)

    def get_doc_footer(self):
        footer_str = '</body></html>'
        return footer_str

    def get_page_footer(self, name, site_url):
        todays_date = date.today()
        year = str(todays_date.year)
        page_footer = '<div class="col">&copy; ' + year + ' All rights reserved to '
        page_footer = page_footer + '<a href="' + site_url + '">' + name + '</a></div>'
        return page_footer

    def get_cover(self, logo, email, phone, site_url, name):
        cover_str = '<div class="container"><div class="row"><div class="col_top"><div class="cantered">'
        cover_str = cover_str + '<div style="width:400px; text-align:center;">'
        if len(logo) > 2:
            cover_str = cover_str + '<img src="' + logo + '" style="width: 100%; object-fit:contain;" />'
        else:
            cover_str = cover_str + '<h1>' + name + '</h1>'
        cover_str = cover_str + '</div>'
        cover_str = cover_str + '<br><br>'
        if len(email) > 2:
            cover_str = cover_str + '<div class="liner_left">' + email + ' </div>'
        if len(phone) > 2:
            cover_str = cover_str + '<div class="liner_right"> ' + phone + '</div>'
        if len(email) < 2 and len(phone) < 2:
            cover_str = cover_str + '<div class="liner_left"> ' + site_url + '</div>'
        cover_str = cover_str + '<br><br><br><br></div></div></div></div>'
        return cover_str

    def get_page_table(self):
        return '<table width="100%" height="860" border="0" cellpadding="0" cellspacing="0">'

    def build_page(self, objs, tpl, name, site_url):
        out_str = ''
        if tpl == 1:
            for obj in objs:
                out_str = out_str + '<div class="container"><div class="row"><div class="col_top">'
                out_str = out_str + self.get_page_table() + '<tr>'
                out_str = out_str + '<td><div class="center">'
                out_str = out_str + self.get_photo(obj, tpl)
                out_str = out_str + '</div></td>'
                out_str = out_str + '</tr></table>'
                out_str = out_str + '</div>' + self.get_page_footer(name, site_url) + '</div></div>'

        elif tpl == 2:
            for idx, obj in enumerate(objs):
                if idx % 2 == 0:
                    out_str = out_str + '<div class="container"><div class="row"><div class="col_top">'
                    pre = self.get_page_table() + '<tr>'
                    post = ''
                else:
                    pre = ''
                    post = '</tr></table>'
                    post = post + '</div>' + self.get_page_footer(name, site_url) + '</div></div>'
                out_str = out_str + pre
                out_str = out_str + '<td style="width:50%;"><div class="center">'
                out_str = out_str + self.get_photo(obj, tpl)
                out_str = out_str + '</div></td>'
                out_str = out_str + post
                if idx == len(objs) - 1 and post == '':
                    out_str = out_str + '<td style="width:50%;"><div class="center"></div></td></tr></table>'
                    out_str = out_str + '</div>' + self.get_page_footer(name, site_url) + '</div></div>'

        elif tpl == 4:
            control_x = 0
            for idx, obj in enumerate(objs):
                if control_x == 0:
                    out_str = out_str + '<div class="container"><div class="row"><div class="col_top">'
                    pre = self.get_page_table() + '<tr>'
                    post = ''
                elif control_x == 3:
                    pre = ''
                    post = '</tr></table></div>' + self.get_page_footer(name, site_url) + '</div></div>'
                elif control_x == 2:
                    pre = '</tr><tr>'
                    post = ''
                else:
                    pre = ''
                    post = ''
                control_x = control_x + 1
                if control_x == 4:
                    control_x = 0
                out_str = out_str + pre
                out_str = out_str + '<td style="width:50%;"><div class="center">'
                out_str = out_str + self.get_photo(obj, tpl)
                out_str = out_str + '</div></td>'
                out_str = out_str + post
                if idx == len(objs) - 1 and post == '':
                    rest = 4 - control_x
                    for i in range(0, rest):
                        out_str = out_str + '<td style="width:50%;"><div class="center"></div></td>'
                        if control_x == 2:
                            out_str = out_str + '</tr><tr>'
                        control_x = control_x + 1
                    out_str = out_str + '</tr></table>'
                    out_str = out_str + '</div>' + self.get_page_footer(name, site_url) + '</div></div>'

        return out_str

    def compose_pdf(self, init_obj):
        start_time = time.time()
        photos = getattr(init_obj, 'photos')
        name = getattr(init_obj, 'name')
        email = getattr(init_obj, 'email')
        phone = getattr(init_obj, 'phone')
        logo = getattr(init_obj, 'logo')
        pics_in_page = int(getattr(init_obj, 'pics_in_page'))
        site_url = getattr(init_obj, 'site_url')

        # build the HTML
        output = self.get_doc_header(name + ' - My Lightbox')
        output = output + self.get_cover(logo, email, phone, site_url, name)
        output = output + self.build_page(photos, pics_in_page, name, site_url)
        output = output + self.get_doc_footer()
        # print(output)

        options = {
            'page-height': '210mm',
            'page-width': '297mm',
        }
        # configure pdfkit to point to wkhtmltopdf layer
        config = pdfkit.configuration(wkhtmltopdf=r"/opt/bin/wkhtmltopdf")
        pdf_name = name + '-Lightbox_' + self.release_id() + '.pdf'
        local_filename = f'/tmp/{pdf_name}'
        if dry_run:
            local_filename = f'{pdf_name}'

        pdfkit.from_string(output, local_filename, configuration=config, options=options)

        end_time = time.time()
        duration = 'Created pdf in ' + str(end_time - start_time) + ' seconds'
        print(duration)
        logger.info(duration)

        return local_filename


def upload_file_to_s3(bucket: str, filename: str) -> Optional[str]:
    """Uploads the generated PDF to s3.

    Args:
        bucket (str): Name of the s3 bucket to upload the PDF to.
        filename (str): Location of the file to upload to s3.

    Returns:
        The file key of the file in s3 if the upload was successful.
        If the upload failed, then `None` will be returned.
    """
    if dry_run:
        return 'returned key..'

    file_key = None
    try:
        file_key = filename.replace('/tmp/', 'pdf/')
        s3_client.upload_file(Filename=filename, Bucket=bucket, Key=file_key)
        logger.info('Successfully uploaded the PDF to %s as %s' % (bucket, file_key))
    except ClientError as e:
        logger.error('Failed to upload file to s3.')
        logger.error(e)
        file_key = None

    if file_key != None:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': destination_bucket,
                'Key': file_key
            },
            ExpiresIn=3600,
        )
        return url

    return file_key


def lambda_handler(event, context):
    if type(event) == str:
        event = json.loads(event)
    logger.info(event)

    if hasattr(event, 'data'):
        ev_data = getattr(event, 'data')
    else:
        ev_data = event['data']

    if type(ev_data) == str:
        ev_data = json.loads(ev_data)

    if hasattr(ev_data, 'photos'):
        photos = getattr(ev_data, 'photos')
        name = getattr(ev_data, 'name')
        email = getattr(ev_data, 'email')
        phone = getattr(ev_data, 'phone')
        logo = getattr(ev_data, 'logo')
        pics_in_page = getattr(ev_data, 'pics_in_page')
        site_url = getattr(ev_data, 'site_url')
    else:
        photos = ev_data['photos']
        name = ev_data['name']
        email = ev_data['email']
        phone = ev_data['phone']
        logo = ev_data['logo']
        pics_in_page = ev_data['pics_in_page']
        site_url = ev_data['site_url']

    my_init_obj = InitObj(
        photos=photos,
        name=name,
        email=email,
        phone=phone,
        logo=logo,
        pics_in_page=pics_in_page,
        site_url=site_url
    )
    composer = PdfComposer()
    pdf_file = composer.compose_pdf(my_init_obj)
    file_key = upload_file_to_s3(destination_bucket, pdf_file)

    if file_key is None:
        error_message = 'Failed to generate PDF.'
        logger.error(error_message)
        return {
            'status': 400,
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "error": error_message,
                "statusText": "error"
            }
        }

    return {
        'status': 200,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {
            "url": file_key,
            "statusText": "success"
        }
    }
