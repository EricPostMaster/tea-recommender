# Tea Recommender System

Welcome to my tea recommender repo! Because this is a pretty new project, the README is serving as a development journal of sorts. Once the project is complete, I'll put it elsewhere in the repo and replace it with something more like I have in my other repos (check them out!).

**12/20/22 - Mercy me, what a headache...**
This is why I can't have nice things. A couple of days ago I was writing new functions and growing the user dictionary, when I suddenly realized that the `all_urls` list was the wrong length. It had been over 1000 items long, and suddenly it was 30. Uh oh... Turns out, I had modified the `get_first_user` function just a bit to allow it to take a specific user URL input, thereby adding/updating a specific user in the data. What a great idea, right?! Well, it turns out there is a small problem with that. In that function, I set `self.all_urls` equal to the followers of the individual being scraped, which instead of updating the list just erases it and starts all over again. Also, it somehow broke the `self.user_dict`, but I was too frustrated to do a full _post mortem_. I just kind of scowled and grumbled at my computer for a while until my wife made me sit by her on the couch and decompress. Then I went and played Nintendo with some friends. Minigames are a good way to blow off some steam.

Anyway, my first attempts at reverting the offending commits were not good. I got stuck in what I'm calling "revert hell" in GitHub Desktop, where nothing I did seemed to actually make meaningful changes to the repository. After stewing about it for a couple of days, I googled a few things tonight and thought that instead of reverting the most recent commits, I might just be able to revert to a _specific_ commit. And indeed that is possible with `git reset`! Huzzah! :tada:

With my newfound but as-yet-untested knowledge, I reset the repository to the commit that I wanted, put those changes on a new branch (`correct-rollback`), and then merged that branch with the `main` branch on GitHub. A couple things were still missing when I updated the `main` branch locally, but I just copied and pasted those things from the commit details in GitHub. NBD.

Now it's time to test everything and see if it's working. I need to figure out how to test this, but for now I'm pretty sure I can just add/update one user at a time and make sure everything adds up correctly.


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

