# Tea Recommender System

Welcome to my tea recommender repo! Because this is a pretty new project, the README is serving as a development journal of sorts. Once the project is complete, I'll put it elsewhere in the repo and replace it with something more like I have in my other repos (check them out!).

**7/3/22 - A repo at last!**  
I've been working on this project for several days now (maybe two weeks?). Late last night I made my first visualization showing both teas and reviewers where the two different entities are different colors, so I was really about that. It's in the [working notebook](https://github.com/EricPostMaster/tea-recommender/blob/main/notebooks/steepster_project.ipynb) if you want to check it out.

Today I decided to make a proper GitHub repo so I can share this and my progress over time. I still want to create functions for scraping, probably within a class of some sort so I can easily create new instances to grow the dataset/update data. However, because I want to keep up momentum and make progress on an MVP, I'm going to switch gears now and start using the Surprise library to make some recommender models. A recommender system was my original goal with this project, so I'm excited to get going on it! I'm also looking forward to incorporating elements of network analysis into the recommendations to see how that might make the model more interesting.

**7/4/22 - Recos all around** 
Last night and this morning were totally recommendation-focused. I made my first models with Surprise, which was exciting. That said, there's way more to it than just fitting models, so I spent some time today reading my Recommender Systems text book to get a better understanding of neighborhood-based collaborative filtering. The main topics were:
* user-based prediction
* item-based prediction
* calculating similarity with Pearson and Cosine
* Adjusting similarity measures through centering
* "Inverse Rating Frequency", not sure if that's an official name, but it's the same idea as Inverse Document Frequency

So much to learn! I'm really excited to start putting all these pieces together and trying out different hyperparameters to get a solid model going.

**7/5/22 - Item-based methods are taking some extra work to understand**  
I'm not feeling great today, so I'm just doing some reading and reviewing. For some reason, I am struggling to imagine item-based collaborative filtering. User-based is intuitive for me, "People like you also enjoyed...". I can envision the User-Item matrix in my head and see how the different columns work together to inform the final outcome.

I think item-based methods are counterintuitive because they compare along rows instead of down columns. I'm so used to looking down columns in my work to see an outlier or a missing data point, but I spend much less time looking across rows in my daily work because usually looking across rows means looking across different attributes, and those attributes are often only loosely related (e.g., expected revenue and marketing channel).

One of the things I'm most interested in with recommender systems is the idea of recommending things that broaden one's perspectives. Terms used to describe this include novelty, diversity, and serendipity. The book I'm reading says that while item-based methods are good for suggesting relevant items, user-based methods are better for providing diversity. That makes sense to me because if I think about my own musical tastes, I tend to listen to a rather thin slice of the universe of music that I might possibly enjoy. If an item-based recommender were used for me, I'd quickly find myself in an echo chamber, and I might get bored. However, other people who like the same music I do might also be music buffs, and I can benefit from their habit of looking for independent bands to discover and enjoy by taking recommendations from their listening histories. 






