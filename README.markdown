#Talking Papers

project home: http://talking-papers.org
repository address: http://github.com/unthinkingly/talkingpapers
project status: early development


#Relationship to walkingpapers

Talkingpapers is based on the "walkingpapers" project with Open Street Map. Here's concept of walkingpapers in one sentence: Print maps on special "walkingpaper," draw on them, scan them back in and help OpenStreetMap improve its coverage of local points of interests and street detail.

By contrast, the concept of talkingpapers: 

Print surveys on "talkingpaper," get people to answer them, scan your results and automatically sync all of your results, even when you change the survery questions.
 
Talkingpapers (unlike walkingpapers, and open street map) is not intended to be a general purpose resource: we are designing narrowly for use by a field assessment team with a logistics team, in a crisis.

We intend to use walkingpapers with each deployment of talkingpapers.

#Project status and licensing

Talkingpapers are currently in conceptual stage of development. The project is Open Source.

#Definition

Talkingpapers are forms that contain special encoded information about the form that you are editing. The paper, by virtue of it's barcodes, contains all of the information about the schma that it represents. It also uses a OCR friendly format known as "those annoying bubble blocks invented by the IRS." This combination of machine readable (ORC) and machine understandable (embedded schema) permits faster and more reliable data transfer. 

#Goals 

The talkingpapers are intended to 1.) reduce the amount of manual data entry that occurs, and 2.) to make it easier to iterate the design of your schema in real time.

#Talkingpapers Audience 

We are designing for relief workers who are generating actionable logistics data in a crisis.

In the UN humanitarian community (eg, nutrition cluster, health cluster, security cluster), organizations have different responsibilities and based on what they known from reports on the ground, so they will do an assessment -- a form. 

Logistics officer: needs to get things from point a to point be in the maximum way (balance of supplies, saftey.)
- what are the supply needs. 
- what kinds of routes are open
- is sombody gonna kill us if we go to the well?

The talkingpaper user is concerned with gathering "relief data"
- critical infrastructure
- condition of the health standpoint
- water and sanitation

These data points are gathered as quickly as possible in order to make actionable conclusions about where to send relief, and how to send it. 

We want to make the forms smarter, so they can make better decisions.

#Information response in a diaster
There are limited avenues for gathering data in a crisis.

 - online
    - sms
    - pda
    - pc
    - etc

  - offline
    -  police
    -  radio
    -  packet radio adapter on sms
    -  HF radio (thought sadly it sits on the shelf, could be synching databases.)
    - etc

Talkingpapers seeks to add a new item to this list (actually to both lists) that is mostly only useful in some particular crisis situations, where other forms of offline access are not easily usable, and there are no magical PDA applications that obviate the basic benefits of paper.



#Scope of software developmet 

Minimally we will need to develop two pieces of software: 

###Talkingpaper Writer
  This is the interface that you use to build a special form that has 2-D barcodes (encoding the schema and revision metadata), 1-D barcodes (encoding particular fields in the schema, associating them with OCR-friendly response areas).
  
###Talkingpaper Reader
  This is the backend that stitches the answers together and correclty associates them with the correct version of the schema, making it possible to rapidly publish many verisons without fear of losing your work.


#Technical Approach

- We use walkingpapers in tandem with talkingpapers
- Presumably there is other OSS that can be used (particularly barcode tools)
- We need to build something first that can be put together in a week, then iterate with a real data cycle.
- We could use the drupal form builder, but nobody really likes using Drupal. 
- We could prototype it with drupal and move away from it.
- We could scratch it together.



#Logistic worker use context

A typical staff guiding the work of a relief logistics workers.

- 10 international staff
- 10 local staff
- 3 guys at the warehouse
- 3 people at the country office
- people ordering supplies
- coordinating between NGOs
- not just depending on their own routes ... perhaps working with CARE or Worldvision ... they share information - about where you can drive and where you can't.


Core use scenario: In a jeep, after a disaster, perhaps a 2-person team driving aorund and researching conditions all day so they can tell where to bring in supplies.

#Situations our users face

- Driving around is tough when everything is broken and people are trying to kill you. 
- Dealing with setting up a camp. 
- Aftershocks
- People who need medication
- Latrines
- Tents
- Rations
- Who is here?
- Who is missing?
- Where are people going to go
- Eegistering everyone at a camp.
- Designing living conditions for people in really shitty circumstances.
- Aid agencies are starved for data for the response effort.
- Victims are their own first responders.


#Example use case: relief worker in Pakistan, post earthquake

- You are talking to people who need your help. You need to know: does your land even exist? are you scared to go back? why? 
- As the situation on the ground changes, you need to get information about new events. 
- Most of the UN groups ask a similar set of questions: 
- do you have pregnant women? 
- do you have any minors. 
- Some of the data will vary a lot more than the others. 

The core data collection happens with people, using forms to guide the interviews, but forms also can guide independent observation, such as a bridge safety assessment, or a building damage checklist.

In this way, a schema/model/ontology is represented in forms used to collect data. The schema is the basis for extremely important decisions, such as: 

- where to send water/firewood/tents/vaccines/etc
- where not to send people because of dangers
- where and when to return for followup support
- where the worst and best is
- tracking "haves" and "needs"

#Example post-distaster timelines

###unsuccessful relief logistics research timeline

A generic view of an unresponsive data cycle: 

DAY ONE: 
Disaster occurs
Relief organization investigates how to help, creates forms
Admisters forms
Makes decisions based on information from forms
DAY TW0
Admisters forms
Makes decisions based on information from forms
DAY THREE
Admisters forms
Makes decisions based on information from forms

(repeat to conclsion of relief effort)


####successful relief logistics research timeline

In this case the forms get better and better from day, exposing the relief organization to information that was not relevant at the time of the initial investigation.

DAY ONE
Diaster occurs
Use the walkinpapers writer to create a form (xforms compatible importer presumably)
Hand out 100 people to use the forms to gather data at the scene.
Scan the forms in and synch the data. 
Update the form based on feedback from your team. 
Sync data.

DAY TWO
Hand out more forms. 
Get more data, update the forms again based on feedback.

DAY THREE
Hand out more forms. 
Get more data, update the forms again based on feedback.
Sync data.

(repeats to conclusion of relief effort)

#Potential for grassroots distaster relief coordination

This data is traditionally ruled by large instutions, but there is a space with talkingpapers for smaller teams of diaster relief efforts (eg, NERTS in san francisco) to work together on collecting valuable survey disaster, because they can share their schemas with other groups that are using talkingpapers.


#Ideas we hold dear

###"Form changes come from the edges not the center." 

People in the field need to give their input on the success of the form, and the administrators need to be able to update their forms without losing their work.  Some of the questions have to change, and some of the questions you *do not have on the form yet* are essential. You are collecting something and the metadata is constantly evolving. Currently the forms are manually entered, sometimes carried over USB over land and then imported into the database. We believe we can improve this cycle and make it possible to have better response times.

###"Manual data entry kills data"

Most of the time that the chance you are sitting in the tent scrubbing they data at night.  The Kirkpatrick law says that your likelyhood of correcting data in a tent all night on the scene of a crisis is direclty proportional to your seniority in a relief organization attenting the crisis. 

###Paper is successful for good reasons, and can be improved
We need paper. Not Piles and piles of it laying around gathering dust. And not the manual transription part. But we need paper-based data in situations where there is no other reasonable option. Data transition points in the crisis ecosystem RUIN data -- most prone to errors in transcriptions. But paper works well in the field; and a completely digital automation is not possible everywhere.


#TODOs 

### Write code
See the spec and the roadmap.

### Write more explainer material
A page that represents the idea and who we are designing it for, to get some understanding of what we are talking about. Then get people who have ideas for how this could be used in other ways, or feedback on what robert is sayin, perhaps they will say "robert is on crack." We should find out. 

### Implementing a real data cycle with a paper-baed schema that changes rapidly
 We intened playtest the concept and refine it for production? Get it out in the open as soon as possible and get the data cycle working. Take input, record input (with OCR), scan the schema, edit the schema, print new forms, scan those, synch the schemas. 

#Longer term goals
The current talkingpapers model is to *acknowledge that there also are many questions you didn't know to ask* thus requiring extremely flexible tools, for iteration in the field during crisis response.

Eventually we also hope to expand our goals to help *recognizing that other people can help you ask better questions*. That is, we hope to proide cross-network schema sharing as well as internal schema sharing.

#PS We could use some help here
- UI designers
- backend coders
- paper scripters
- playtesters
