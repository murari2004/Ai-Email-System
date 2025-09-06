import imaplib, email
from email.header import decode_header
from typing import List, Dict
import re
from app.core.config import IMAP_HOST, IMAP_USER, IMAP_PASS

SUPPORT_KEYWORDS = ['support','help','query','request','issue','problem','error','assist']

class EmailService:
    def __init__(self):
        pass

    def _decode_header(self, hdr):
        if not hdr: return ''
        dh = decode_header(hdr)[0]
        val = dh[0]
        enc = dh[1] or 'utf-8'
        if isinstance(val, bytes):
            try:
                return val.decode(enc, errors='ignore')
            except:
                return val.decode('utf-8',errors='ignore')
        return val

    def fetch_imap(self, folder='INBOX', max_results=50) -> List[Dict]:
        # Requires IMAP_HOST, IMAP_USER, IMAP_PASS set in ENV
        if not IMAP_HOST or not IMAP_USER or not IMAP_PASS:
            return []
        m = imaplib.IMAP4_SSL(IMAP_HOST)
        m.login(IMAP_USER, IMAP_PASS)
        m.select(folder)
        status, data = m.search(None, 'UNSEEN')
        if status != 'OK':
            m.logout()
            return []
        ids = data[0].split()
        ids = ids[::-1][:max_results]
        results = []
        for idb in ids:
            status, msg_data = m.fetch(idb, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            subject = self._decode_header(msg.get('Subject'))
            sender = self._decode_header(msg.get('From'))
            date = msg.get('Date')
            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp = str(part.get('Content-Disposition'))
                    if ctype == 'text/plain' and 'attachment' not in disp:
                        try:
                            body = part.get_payload(decode=True).decode(errors='ignore')
                            break
                        except: pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                except: body = ''
            results.append({'provider_id': idb.decode(), 'sender': sender, 'subject': subject, 'body': body, 'received_date': date})
        m.logout()
        return results

    def filter_support(self, items: List[Dict]) -> List[Dict]:
        out = []
        for it in items:
            text = (it.get('subject','') + ' ' + it.get('body','')).lower()
            if any(k in text for k in SUPPORT_KEYWORDS):
                out.append(it)
        return out

    def extract_info(self, body: str) -> Dict:
        info = {'phone': None, 'alt_email': None, 'product_mentions': []}
        # phone
        phone = re.findall(r'\b\+?\d[\d \-()]{7,}\b', body)
        if phone:
            info['phone'] = phone[0]
        # emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', body)
        if emails:
            info['alt_email'] = emails[0]
        # product mentions (customize)
        products = ['product1','product2','service1','service2']
        for p in products:
            if p in body.lower():
                info['product_mentions'].append(p)
        info['product_mentions'] = ','.join(info['product_mentions'])
        return info
