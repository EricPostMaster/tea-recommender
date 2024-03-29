# Tea Recommender System

Welcome to my tea recommender repo! Because this is a pretty new project, the README is serving as a development journal of sorts. Once the project is complete, I'll put it elsewhere in the repo and replace it with something more like I have in my other repos (check them out!).

**2/7/23 - Automated scraping is live at last!!!**

Wow. It has been a long month, but I've got something awesome to show for it: I've got an automated Lambda function scraping and storing data on a schedule! It’s humming along with its Docker container, pulling new data every hour, and logging it in glorious, if not nauseating, detail.

It has been a difficult but worthwhile journey. What started out as, “Oh sure, I’ll just pop the code into Lambda and get/put data in an S3 bucket” turned into an deep dive into Lambda layers, Docker, CloudWatch, and Serverless. I’m even starting to understand what a YAML file does, which has befuddled me for some time now. Side projects are my favorite.

**My First Idea**

My initial setup idea was putting the existing network dictionary pickle file into an S3 bucket and then scheduling the Lambda function to pull from that bucket, scrape, and then save the updated file back in S3, overwriting the original file.

Turns out, that was a dramatic oversimplification, and Selenium is the culprit.

**Layers & Containers**

Scraping data with Selenium requires the Selenium library (duh) and Chromedriver, neither of which are default Python packages. Lambda functions only run with default Python modules and a number of libraries selected by AWS. The first approach I found is to create a layer for each of the extra modules required and connect the layer(s) to the function. I followed [this tutorial](https://dev.to/awscommunity-asean/creating-an-api-that-runs-selenium-via-aws-lambda-3ck3), but I gave up after I kept getting Chromedriver errors. Instead, I used a Docker container.

Creating a Lambda function using a Docker container circumvents the need for layers because everything is built into the container. I was so excited when I found this [GitHub repo by Umihico](https://github.com/umihico/docker-selenium-lambda/), which provides a Docker image specifically for headless Chrome and Selenium as well as a Serverless YAML file to build the container on ECR. I added a schedule to the function in the file as well as an IAM role provision so the function can get/put objects in the correct S3 bucket. I know it's a little thing, but I felt really proud for doing both of those things because I've never worked with a YAML file before. Side note: the [Serverless framework docs](https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml) are great.

**Summary - Important Learnings**
- How to get and put objects from an S3 bucket
- Setting up basic IAM roles for the related service
- Creating Lambda layers
- Deploying with Serverless framework
- Managing deployment from the CLI on local machine
- Scheduling Lambda functions through the serverless.yml file as well as in AWS settings

**Next Steps**

Now that the scraper is chugging along, I'm going to turn my focus into getting the network dictionary file into a database. I've been considering using AWS Neptune following [this tutorial](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-data.html) (plus whatever else I need from StackOverflow), but I'm also going to explore DynamoDB because I'm not sure whether a graph or NoSQL database would be a better fit.

**Parting Thought**

If you happen to be reading this and feeling like I have made this look easy, I want to be absolutely clear: This explanation is just a few paragraphs long, but the real-life process was filled with false starts, small successes, and seemingly endless new error messages. It's very easy to quit along the way (I have before), but I'm so glad I stuck with it. I learned good things and feel much more confident exploring new AWS services.



**1/8/23 - Not-quite-unique identifiers**  
So, like I mentioned yesterday, I haven't worked on the `TeaDict` class in a while. Somehow, my `get_teas` method stopped collecting URLs. Not sure why because I don't think the page code has changed, but it is what it is!

The main thing I re-learned while fixing the `get_teas` method was how to locate a set of repeating chunks of code using the `find_elements` Selenium method and then drill down into them individually using a `for` loop. Here's an example of what I mean:

```python
# XPath to the root node
tea_xpath = "//div[@class='product tea']//div[@class='tea']"

# find_elements returns a list of each occurrence of the root node
tea_root =  driver.find_elements(By.XPATH,tea_xpath)

# within each root node ('tea' in this loop), there's an element
# with the class 'tea-name', so I grab its href value
for tea in tea_root:
  tea_link = tea.find_element(By.CLASS_NAME,'tea-name').get_attribute("href")
```

Once I got that fixed, I noticed that there were a couple of teas that weren't being scraped correctly, specifically Irish Breakfast and Earl Grey, both of which are common and popular teas. After a bit of puzzling, I realized that I had made a silly mistake: I was using a non-unique tea name as the dictionary key for the master tea dictionary. Doh! :man_facepalming: Every major tea brand has an Earl Grey, so only the first one would have been captured if I had ignored it and continued scraping. Major flavors like that are popular and have many ratings, so that would have been terrible for my network data!

I noticed all of this pretty late in the evening, so I'm going to bed and will work on it after I've gotten some sleep 😴 I'll need to delete the tea dictionary that I have and start over, but I only had a few dozen teas scraped, so it's not a big deal. The code updates to use a unique identifier for each tea should be pretty straightforward, so I'm grateful for that. Despite these issues, coming back to the `TeaDict` class a few months after working on it has shown me that I've learned a lot since then, so I feel good about that.


**1/7/23 - Flavor of code**  
Now that the user dictionary is pretty much done, today I decided to work on adding flavors to the tea dictionary. I haven't really worked on the tea dictionary in a long time, so I was worried I wouldn't be able to make sense of my code. Fortunately, the `TeaDict` class is quite a bit simpler than the `UserDict`, so I was able to jump in pretty quickly.

My original idea for the tea dictionary was just to have the tea name, URL, overall rating, and then individual ratings by users. Then, over Christmas break I was reading about embeddings and thought that a flavor embedding would be a really cool, non-ratings way to find similarities between teas. Also, each tea happens to have a nice, comma-separated list of flavors that are added by users, so it's a no-brainer!

A couple of interesting things happened when I started working on it:
1. None of my Selenium `driver.find_element_by` methods were working. Turns out, I had updated to Selenium 4 in order to fix a VSCode issue, and a side effect is that the `find_element_by` methods have all been deprecated! Fortunately, somebody made [this handy comment](https://github.com/SeleniumHQ/selenium/pull/10712#issuecomment-1255097016) for finding and replacing the old methods with the new ones.
2. The flavor list is inside a `<dl>` HTML tag, which is a new one for me. Nothing a little [W3 Schools research](https://www.w3schools.com/tags/tag_dl.asp) can't fix! Turns out `dl` is a "description list", and its sub-elements are `dt` (terms) and `dd` (definition/description). The tricky part for me was that `dt` and `dd` do not have a parent-child relationship; they have a sibling relationship, which was new to me. After some StackOverflow research, I put together this XPath: `"//dl[@class='tea-description']/dt[text() = 'Flavors']/following-sibling::dd"`, which finds the description section, then the Flavors term and its flavor list. I'm still not sure what the double colons are at the end, but it works like a charm. Also, I think that `text() =` thing is definitely going to come in handy later.


**1/4/23 - (Pretty much) all users scraped!**  
I've been on vacation for the past few days, so I've taken advantage of the wicked fast wifi here in our Airbnb to scrape lots of data. I think I've completed the entire user dictionary, which is really exciting! As far as I can tell, there are about 8100 users in the network, and about 6300 of them have followers. The other 1800 (including myself) don't have any followers; we only follow other people.

One major limitation of building a network by scraping followers, followers' followers, etc. is that if there is an island in the network, I can't get to it. There could be another group of 50 highly connected and highly active people that I can't see because they are completely disconnected from the rest of the network. That said, I think it's unlikely that there is an invisible group of highly active users.

It's very possible that there are highly active individuals. They might be highly active tea reviewers but not inclined to follow others. If I want to, I could find them through tea reviews, where I am capturing the names of all individuals who review a tea. Their reviews will be helpful for recommending teas to other users, even if their folling/follower data isn't particularly useful.

Anyway, for now I'm just stoked to have a full user dictionary. I re-ran my Jaccard coefficient follow recommender, and the precision at k increased significantly, which I expected because I have a lot more connections to work with. I went from ~2% to a little over 4% at _p@10_, and that is for all users, so 100% coverage!


**12/27/22 - Better precision**  
Today I focused on improving my _p@k_ from yesterday instead of making any new recommendations. There wasn't much to improve upon: my top precision was around 1.6 percent or something. **#Dismal**

I started by adding a dictionary to my big list of p@k for each user. That way, I could see which users were having the most trouble. User `NimSeegobin` is a good example. He is only following three people, and two of them are in the training graph. When I look at the top recommendations per the Jaccard index, the coefficients are correct, but `NimSeegobin` follows so few people that it's nearly impossible to predict the 1 other user that we don't already know. Also, `NimSeegobin` isn't even in the test dataset, so recommendations for him will always be wrong, dragging down the average precision. What's a data scientist to do?!

Well, I decided to continue calculating Jaccard coefficients using the entire training dataset, but I would only check nodes in the test data if the user follows at least _X number_ of users (`G.out_degree(user)`) in the overall dataset. (I'm 98% sure that isn't data leakage.) I started out at a threshold of 20 followwing, but I also tried different levels. It generally gets better as I get more stringent in the required following number, but there are also far fewer users who are following that many people (figure 1 below). Maybe there's something like an elbow plot where if I plot the avg overall p@k for different test following numbers? Still thinking about that one.

**Figure 1**  
![out-degree distribution chart (loglog axes)](https://raw.githubusercontent.com/EricPostMaster/tea-recommender/main/images/out_degree_distribution.png "out-degree distribution chart (loglog axes)")

As you can see, many people follow very few people, so recommending people to follow based solely on the people the follow mutually with others is probably not going to work well! Next step there will be to serve up something like the most popular users. `teaequalsbliss` comes to mind quickly because she has a ton of followers.

Anyway, after all that research, I implemented that threshold I mentioned earlier, and my precision improved dramatically! Here's an example of no restriction vs. requiring users to follow at least 30 people:

| Following Threshold = 1        | Following Threshold = 30           |
| ------------- |:-------------:|
| ![p@k chart with following threshold = 1](https://raw.githubusercontent.com/EricPostMaster/tea-recommender/main/images/precision_at_k_threshold1.png "p@k with following threshold = 1")     | ![p@k chart with following threshold = 30](https://raw.githubusercontent.com/EricPostMaster/tea-recommender/main/images/precision_at_k_threshold30.png "p@k with following threshold = 1") |

If you look past the non-synchronized y-axes, you'll see that the p@k for the lower threshold tops out at about 1% and bounces around pretty randomly. On the other side, at a minimum following threshold of 30 users, precision starts out at 10%, which is very exciting considering I couldn't top 2% yesterday! 🥳 The drawback, as you may have noticed is a significant reduction in the number of users who would be served personalized recommendations. In the first group, 100/100 would receive (lousy) recommendations. In the second group, only 30/500 followed enough other users to make the cut. It would be nice to provide personalized recommendations to at least 10% of users at at least 10% p@1, but we'll see if that's realistic. Now that I'm getting into better precision range, I may consider Mean Average Precision (MAP) from chapter 9 of PRS.

For now, it's late, and I'm going to bed! 😴

**12/26/22 - First decent recos!**
I spent so much time working on this project today, and it was great. I've got some new resources to help me along the way: I bought _Practical Recommender Systems_ (PRS) by Kim Falk and _Graph Machine Learning_ by Stamile, Marzullo, and Deusebio for Christmas, so I've been reading a fair bit over the last few days.

I've decided that the first bit of work I wanted to do with the network data I've been scraping is just recommending users for people to follow. It's simple, unary data (either you follow them or you don't), so I decided to use the Jaccard index to sort recommendations and as a basis for making predictions. I'm very pleased with the outcome so far!

There is definitely a lot more analysis to be done, but I think one of the biggest things I need to figure out is what the minimum level of connectivity is in the graph in order to be included in the recommendation generator. Many users don't follow anyone, and so it drags down the overall precision because they have 0 similarity to anyone else. Lame. I believe that issue is discussed in chapter 7 of PRS, so I'm definitely going to check it out. I can probably just recommend some top power users for new folks who don't follow anyone, just to get started. Eventually I could build something with node embeddings and ask people to give me some info to overcome the cold start problem, but for now I just want to get them out of my data! 😅

Anyway, I think next steps will be cleaning up the input data and dealing with outliers so I can get a better idea of what kind of precision I get with average and highly active users. I'm also definitely open to other measurements of similarity. I just went with Jaccard because it was in my books, I could understand it, and the code to implement it wasn't too bad.


**12/25/22 - An unexpected Christmas side quest**
I had an unexpected adventure today. I tried to use the `jaccard_coefficient` function in NetworkX and found that it hasn't been implemented on directed graphs! Whaaaa?! So I decided to look into it. There was an issue opened up a while ago about it, and the consensus from the maintainers was that it doesn't need to be restricted to undirected graphs only, so they invited the person who opened the issue to submit a PR, which he never did. Hooray, opportunity for me to contribute!

Turns out, it wasn't even that hard. The `common_neighbors` function that the `jacard_coefficient` function uses was not implemented on directed graphs, so I went through all the contributor stuff, edited the functions, and submitted a PR for it. I'm super stoked! Interestingly, I didn't have to edit any of the code; I just made it clear that the neighbors referred to in a directed graph are the targets of the node in question. Hopefully it gets merged soon. In the meantime, I'm implementing my own Jaccard coefficient function so I can keep working on my project!


**12/20/22 - Mercy me, what a headache...**
This is why I can't have nice things. A couple of days ago I was writing new functions and growing the user dictionary, when I suddenly realized that the `all_urls` list was the wrong length. It had been over 1000 items long, and suddenly it was 30. Uh oh... Turns out, I had modified the `get_first_user` function just a bit to allow it to take a specific user URL input, thereby adding/updating a specific user in the data. What a great idea, right?! Well, it turns out there is a small problem with that. In that function, I set `self.all_urls` equal to the followers of the individual being scraped, which instead of updating the list just erases it and starts all over again. Also, it somehow broke the `self.user_dict`, but I was too frustrated to do a full _post mortem_. I just kind of scowled and grumbled at my computer for a while until my wife made me sit by her on the couch and decompress. Then I went and played Nintendo with some friends. Minigames are a good way to blow off some steam.

Anyway, my first attempts at reverting the offending commits were not good. I got stuck in what I'm calling "revert hell" in GitHub Desktop, where nothing I did seemed to actually make meaningful changes to the repository. After stewing about it for a couple of days, I googled a few things tonight and thought that instead of reverting the most recent commits, I might just be able to revert to a _specific_ commit. And indeed that is possible with `git reset`! Huzzah! :tada:

With my newfound but as-yet-untested knowledge, I reset the repository to the commit that I wanted, put those changes on a new branch (`correct-rollback`), and then merged that branch with the `main` branch on GitHub. A couple things were still missing when I updated the `main` branch locally, but I just copied and pasted those things from the commit details in GitHub. NBD.

Now it's time to test everything and see if it's working. I need to figure out how to test this, but for now I'm pretty sure I can just add/update one user at a time and make sure everything adds up correctly.

_[an hour or so later]_

Tested, and everything is working again!!! 🥳 I was able to get new users and update an existing user without messing up the base datasets. I'm very relieved.

Two potential next steps:
* Grow this user dataset and start making some recommendations with it
* Improve the tea dictionary functions. They are very inefficient right now, so growing the dictionary 10x will take a relatively long time and consume a lot of data, and that's not even very much data to add to the dictionary. I don't want to grow that dataset until the functions are more efficient.

I think I'm going to focus on growing the user dataset and doing some reco work with it. That will feel good.


**12/16/22 - I'm back!**
It's been a while since I've worked on this project, and I'm glad to be back at it. I took a break for a bit to work on my Fortune Cookie Movies project, move to Utah, and just generally take a break because I've been feeling a little burnt out. Anyway, I'm ready to get back into this.

One thing I want to say about this now that I'm getting back to it - comments and docstrings are the BEST! I would have been completely lost if not for the docstrings I wrote on my functions. It helped prime my brain and get back in the zone.

I've created the `UserDict` class, which I'm really excited about because it was just a couple of blocks of code in a Jupyter notebook before.

I've got two potential items to work on next:
* Automate scraping, like with a server or something. I'm not very familiar with how to do this, and it's kind of overwhelming
* Write a function that will scrape more info about an existing user. For example, if user 'eric' has 50 followers, but I've only scraped info on 30 of them, I want to be able to go and scrape the other 20 as well.

**7/10/22 - Back to scraping**  
I decided to go back to my scraping code yesterday because it was only stored in a Jupyter notebook. I created a `TeaDict` class that I think is awesome! Here's what it can do so far:
* `get_teas` method: Scrapes tea names, brands, and URLs from Steepster tea overview page.
* `get reviews` method: Gets reviewer names and ratings for each tea.
* `save_tea_dict` method: Pickles the tea_dict data for later use.

There's definitely room for improvement; for example, the `get_reviews` method is pretty long and can probably be broken into a couple of sub-functions. Even so, I'm really pleased with how it is turning out.  

One of the most important updates is that now I can easily import the data and either update existing entries with more reviews or add new entries. Before, it started from scratch every time. #Lame

**7/5/22 - Item-based methods are taking some extra work to understand**  
I'm not feeling great today, so I'm just doing some reading and reviewing. For some reason, I am struggling to imagine item-based collaborative filtering. User-based is intuitive for me, "People like you also enjoyed...". I can envision the User-Item matrix in my head and see how the different columns work together to inform the final outcome.

I think item-based methods are counterintuitive because they compare along rows instead of down columns. I'm so used to looking down columns in my work to see an outlier or a missing data point, but I spend much less time looking across rows in my daily work because usually looking across rows means looking across different attributes, and those attributes are often only loosely related (e.g., expected revenue and marketing channel).

One of the things I'm most interested in with recommender systems is the idea of recommending things that broaden one's perspectives. Terms used to describe this include novelty, diversity, and serendipity. The book I'm reading says that while item-based methods are good for suggesting relevant items, user-based methods are better for providing diversity. That makes sense to me because if I think about my own musical tastes, I tend to listen to a rather thin slice of the universe of music that I might possibly enjoy. If an item-based recommender were used for me, I'd quickly find myself in an echo chamber, and I might get bored. However, other people who like the same music I do might also be music buffs, and I can benefit from their habit of looking for independent bands to discover and enjoy by taking recommendations from their listening histories. 

**7/4/22 - Recos all around** 
Last night and this morning were totally recommendation-focused. I made my first models with Surprise, which was exciting. That said, there's way more to it than just fitting models, so I spent some time today reading my Recommender Systems text book to get a better understanding of neighborhood-based collaborative filtering. The main topics were:
* user-based prediction
* item-based prediction
* calculating similarity with Pearson and Cosine
* Adjusting similarity measures through centering
* "Inverse Rating Frequency", not sure if that's an official name, but it's the same idea as Inverse Document Frequency

So much to learn! I'm really excited to start putting all these pieces together and trying out different hyperparameters to get a solid model going.

**7/3/22 - A repo at last!**  
I've been working on this project for several days now (maybe two weeks?). Late last night I made my first visualization showing both teas and reviewers where the two different entities are different colors, so I was really about that. It's in the [working notebook](https://github.com/EricPostMaster/tea-recommender/blob/main/notebooks/steepster_project.ipynb) if you want to check it out.

Today I decided to make a proper GitHub repo so I can share this and my progress over time. I still want to create functions for scraping, probably within a class of some sort so I can easily create new instances to grow the dataset/update data. However, because I want to keep up momentum and make progress on an MVP, I'm going to switch gears now and start using the Surprise library to make some recommender models. A recommender system was my original goal with this project, so I'm excited to get going on it! I'm also looking forward to incorporating elements of network analysis into the recommendations to see how that might make the model more interesting.

