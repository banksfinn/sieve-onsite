# Product Eng Onsite - GTM-Eng Collaboration

## Background

At Sieve, our Engineering and GTM (Go-To-Market) teams collaborate to deliver high-quality video data that aligns with customer requirements. GTM is generally less technical but works more closely with customers, while Engineering has deeper context on our processing stack and can iterate on datasets. Because a single dataset delivery can be petabytes of data, GTM and Engineering use samples to align on dataset status and quality.

These samples often include:

- Videos themselves
- Metadata information for each video
  - Video-level metadata (resolution, fps, etc.)
  - Time-bounded metadata (num_faces, is_full_body, has_overlay, etc.)

Customers often want clips, which additionally means sending portions of the full videos we store according to the time-bounded metadata. Typically, customers manually review samples with researchers to qualify the data, which can number in the thousands of clips.

An example clip metadata file:

```json
{
  delivery_id: "y_VMplMXoqnaY",
	uri: "gs://mybucket/videos/y_VMplMXoqnaY_clip_1.mp4",
	clip_start_time: 1.23,
	clip_end_time: 5.23,
	clip_duration: 4.00, // duration of the scene
	avg_face_size: 125,
	max_num_faces: 2,
	...
},
{
  delivery_id: "y_VMplMXoqnaY",
	uri: "gs://mybucket/videos/y_VMplMXoqnaY_clip_2.mp4",
	clip_start_time: 50.23,
	clip_end_time: 58.23,
	clip_duration: 8.00,
	avg_face_size: 100,
	max_num_faces: 1,
	...
},
{
  delivery_id: "y_b9plMXe89G",
	uri: "gs://mybucket/videos/y_b9plMXe89G_clip_1.mp4",
	clip_start_time: 10.23,
	clip_end_time: 16.23,
	clip_duration: 6.00,
	avg_face_size: 120,
	max_num_faces: 2,
	...
},

```

Example video level metadata

```json
{
  delivery_id: "y_b9plMXe89G",
	fps: 29.9
	height: 1080
	width: 1920
	source: "web"
	language: "en"
	...
},
{
  delivery_id: "y_VMplMXoqnaY",
	fps: 30
	height: 1080
	width: 1920
	source: "visora"
	language: "fa"
	...
},

```

There is often iteration between Engineering and GTM in the process before delivering anything to a customer.

This process is integral to GTM’s ability to close a deal. The smoother the process is on both ends, the faster we can get the right, accurate data into the customer’s hands

## Problem

Our current process involves:

1. GTM receives a sample bucket and metadata bucket
2. A GTM member downloads the videos from the bucket to view
3. They also have to search the metadata separately for the video
4. This feedback is given back to an engineer who has to do a similar process

This process is tedious for both GTM and Engineering. Both sides lack a good way to view videos and metadata. Additionally, the feedback is not well organized, which adds more iteration time to the deal flow and requires additional work from Engineering.

We want to build a product experience for both GTM and Engineering that makes this workflow as smooth as possible until we finalize a sample set with the customer.

Things to consider:

- How can the review experience be fluid and make the review process as fast as possible?
- How can engineers get effective and usable feedback to potentially update samples accordingly?
- GTM is often simply given a bucket of videos and a metadata file. While we can start here, what’s the ideal process?

Other dimensions to think about:

- Speed
- Cost
- Reliability

Bucket: gs://product-onsite/

## Deliverable

You’ll be expected to build a functioning end-to-end product that will be reviewed together at the end of the day. It should, at minimum, be able to use the given bucket and JSON file to send samples to a potential customer, provide a UI for a customer to view samples, allow customers to provide video-specific feedback, and allow GTM to view that feedback. Samples should also be updatable.

AI tools are welcome, though you should be prepared to talk through your code design at any point. You are free to use whatever frameworks you prefer.

We can provide reimbursement for the use of paid external tools if required.

You may ask for UX feedback from any team members while working or during your coffee chats at any point during the day.

---

## Rubric

You will be evaluated on:

- Your thorough understanding of the problem
- The engineering principles used to create your product
- UI/UX for both GTM and engineering
- Your ability to communicate your solution

Good luck!

