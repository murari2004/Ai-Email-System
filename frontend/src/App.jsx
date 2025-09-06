import React, {useState, useEffect} from 'react'
import axios from 'axios'

export default function App(){
  const [emails, setEmails] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = async ()=>{
    try{
      const res = await axios.get('http://localhost:8000/api/v1/emails')
      setEmails(res.data)
    }catch(e){ console.error(e) }
  }
  useEffect(()=>{ load() }, [])

  const fetchEmails = async ()=>{
    setLoading(true)
    await axios.post('http://localhost:8000/api/v1/emails/fetch')
    await load()
    setLoading(false)
  }
  const process = async ()=>{
    setLoading(true)
    await axios.post('http://localhost:8000/api/v1/emails/process')
    setLoading(false)
    alert('Enqueued processing jobs. Start an RQ worker: rq worker -u redis://localhost:6379')
  }

  return (<div style={{padding:20,fontFamily:'Arial'}}>
    <h1>AI Email Assistant - Complete</h1>
    <div style={{marginBottom:12}}>
      <button onClick={fetchEmails} disabled={loading}>Fetch Support Emails</button>
      <button onClick={process} disabled={loading} style={{marginLeft:10}}>Process (enqueue)</button>
    </div>
    <div style={{display:'flex',gap:20}}>
      <div style={{flex:1}}>
        <h3>Emails</h3>
        <table border="1" cellPadding="6" style={{width:'100%'}}>
          <thead><tr><th>ID</th><th>Sender</th><th>Subject</th><th>Priority</th><th>Processed</th></tr></thead>
          <tbody>
            {emails.map(e=> (<tr key={e.id} onClick={()=>setSelected(e)} style={{cursor:'pointer'}}><td>{e.id}</td><td>{e.sender}</td><td>{e.subject}</td><td>{e.priority||'-'}</td><td>{e.processed}</td></tr>))}
          </tbody>
        </table>
      </div>
      <div style={{flex:1}}>
        <h3>Details</h3>
        {selected ? (<div>
          <p><b>From:</b> {selected.sender}</p>
          <p><b>Subject:</b> {selected.subject}</p>
          <p><b>Body:</b><br/>{selected.body}</p>
          <p><b>Sentiment:</b> {selected.sentiment}</p>
          <p><b>Priority:</b> {selected.priority}</p>
          <p><b>Phone:</b> {selected.phone}</p>
          <p><b>Alt Email:</b> {selected.alt_email}</p>
          <p><b>AI Draft:</b></p>
          <textarea style={{width:'100%',height:150}} defaultValue={selected.ai_response || ''}></textarea>
          <div style={{marginTop:8}}><button>Send Reply (placeholder)</button></div>
        </div>) : <div>Select an email to view details</div> }
      </div>
    </div>
  </div>)
}
