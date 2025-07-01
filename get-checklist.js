export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Only POST allowed' });
  }

  const { businessType, dataCollected, payments } = req.body;

  const checklist = {
    laws: [],
    actions: [],
    riskLevel: "Low",
    links: []
  };

  if (dataCollected) {
    checklist.laws.push("GDPR");
    checklist.actions.push("Register with ICO", "Add Privacy Policy");
    checklist.links.push("https://ico.org.uk/register");
    checklist.riskLevel = "Medium";
  }

  if (payments) {
    checklist.laws.push("Consumer Contracts Regulations");
    checklist.actions.push("Create Terms of Use", "Add Refund Policy");
    checklist.riskLevel = "High";
  }

  res.status(200).json(checklist);
}
{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 export default function handler(req, res) \{\
  if (req.method !== 'POST') \{\
    return res.status(405).json(\{ error: 'Only POST allowed' \});\
  \}\
\
  const \{ businessType, dataCollected, payments \} = req.body;\
\
  const checklist = \{\
    laws: [],\
    actions: [],\
    riskLevel: "Low",\
    links: []\
  \};\
\
  if (dataCollected) \{\
    checklist.laws.push("GDPR");\
    checklist.actions.push("Register with ICO", "Add Privacy Policy");\
    checklist.links.push("https://ico.org.uk/register");\
    checklist.riskLevel = "Medium";\
  \}\
\
  if (payments) \{\
    checklist.laws.push("Consumer Contracts Regulations");\
    checklist.actions.push("Create Terms of Use", "Add Refund Policy");\
    checklist.riskLevel = "High";\
  \}\
\
  res.status(200).json(checklist);\
\}\
}
