import graphene 
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q, Avg, Count, Sum, Max, F
from django.db.models.functions import Greatest
from datetime import datetime

from .models import Trail, Hike, Hiker, Buddy, EquipmentUsed, EquipmentType, SuggestedEquipment, Tag, Friend, Message 

class MessageType(DjangoObjectType):
   mostRecentSent = graphene.DateTime()
   mostRecentReceived = graphene.DateTime()
   mostRecentThreadActivity = graphene.DateTime()
   class Meta:
      model = Message

class FriendType(DjangoObjectType):
   class Meta:
      model = Friend

class TagType(DjangoObjectType):
   class Meta:
      model = Tag

class SuggestedEquipmentType(DjangoObjectType):
   class Meta:
      model = SuggestedEquipment

class EquipmentTypeType(DjangoObjectType):
   class Meta:
      model = EquipmentType

class EquipmentUsedType(DjangoObjectType):
   class Meta:
      model = EquipmentUsed

class TrailType(DjangoObjectType):
   avgDifficulty = graphene.Float()        # place aggregate (derived) values here
   avgEnjoyability = graphene.Float()        # place aggregate (derived) values here
   numHikes = graphene.Int()
   class Meta:
      model = Trail 

class HikeType(DjangoObjectType):
   totalHikerDistance = graphene.Int()
   date = graphene.Date()
   class Meta:
      model = Hike 

class BuddyType(DjangoObjectType):
   class Meta:
      model = Buddy

class Query(graphene.ObjectType):
   trails = graphene.List(TrailType, search=graphene.String())
   hikes = graphene.List(HikeType)
   beginner_trails = graphene.List(TrailType)
   all_equ_types = graphene.List(EquipmentTypeType)
   popular_trails = graphene.List(TrailType)
   trail_details = graphene.List(TrailType, trailID=graphene.Int(required=True))
   expert_reviews = graphene.List(HikeType, trailID=graphene.Int(required=True))
   recent_hikers = graphene.List(HikeType, trailID=graphene.Int(required=True))
   hike_detail = graphene.Field(HikeType, hikeID=graphene.Int(required=True))
   conversation_threads = graphene.List(MessageType, hikerID=graphene.Int(required=True))
   thread_detail = graphene.List(MessageType, hikerID=graphene.Int(required=True), recipientID=graphene.Int(required=True))
   hiker_most_recent_hike_on_trail = graphene.List(HikeType, trailID=graphene.Int(required=True), hikerID=graphene.Int())

   def resolve_trails(self, info, search=None):
      if search:
         filter = (
            Q(name__icontains=search) |
            Q(prop__icontains=search) |
            Q(city__icontains=search) | 
            Q(state__icontains=search)
         )
         return Trail.objects.filter(filter)
      else:
         return Trail.objects.all() 

   def resolve_hikes(self, info):
      return Hike.objects.all()

   def resolve_beginner_trails(self, info):
      return Trail.objects.annotate(avgDifficulty=Avg('hikes__difficulty')). \
         annotate(avgEnjoyability=Avg('hikes__enjoyability')).order_by('avgDifficulty')[:15]

   def resolve_all_equ_types(self, info):
      return EquipmentType.objects.all()

   def resolve_popular_trails(self, info):
      return Trail.objects.annotate(numHikes=Count('hikes')).annotate(avgDifficulty=Avg('hikes__difficulty')). \
         annotate(avgEnjoyability=Avg('hikes__enjoyability')).order_by('-numHikes')[:15]

   def resolve_trail_details(self, info, trailID):
      # return Trail.objects.get(id=trailID)
      return Trail.objects.filter(id=trailID).annotate(numHikes=Count('hikes')).annotate(avgDifficulty=Avg('hikes__difficulty')). \
         annotate(avgEnjoyability=Avg('hikes__enjoyability'))

   def resolve_expert_reviews(self, info, trailID):
      return Hike.objects.filter(trail__id=trailID).exclude(review=None).annotate(totalHikerDistance=Sum('hiker__hikes__trail__distance')). \
         order_by('-totalHikerDistance')[:5].annotate(date=F('checkInDate__date'))

   def resolve_recent_hikers(self, info, trailID):
      return Hike.objects.filter(trail__id=trailID).annotate(latestDateForHiker=Max('hiker__hikes__checkInDate', \
         filter=Q(hiker__hikes__trail__id=trailID))).filter(checkInDate=F('latestDateForHiker')).order_by('-checkInDate')

   def resolve_hike_detail(self, info, hikeID):
      return Hike.objects.get(id=hikeID)

   def resolve_conversation_threads(self, info, hikerID):
      return Message.objects.filter(Q(hikerID__id=hikerID) | Q(recipientID__id=hikerID)). \
         annotate(mostRecentSent=Max('hikerID__messagesSent__timeSent', \
         filter=Q(hikerID__messagesSent__recipientID=F('recipientID')))). \
         annotate(mostRecentReceived=Max('hikerID__messagesReceived__mostRecentSent', \
         filter=Q(hikerID__messagesReceived__hikerID=F('recipientID')))). \
         annotate(mostRecentThreadActivity=Greatest('mostRecentSent', 'mostRecentReceived')). \
         filter(timeSent=F('mostRecentThreadActivity')).order_by('-timeSent')

   def resolve_thread_detail(self, info, hikerID, recipientID):
      return Message.objects.filter((Q(hikerID__id=hikerID) & Q(recipientID__id=recipientID)) | \
         (Q(hikerID__id=recipientID) & Q(recipientID__id=hikerID))).order_by('-timeSent')

   def resolve_hiker_most_recent_hike_on_trail(self, info, trailID, hikerID=None):
      trail = Trail.objects.get(id=trailID)
      if hikerID:
         hiker = Hiker.objects.get(id=hikerID)
      else:
         user = info.context.user 
         if user.is_anonymous:
            raise Exception("Not logged in")
         hiker = Hiker.objects.get(user=user)
      hike = Hike.objects.filter(hiker=hiker, trail=trail).order_by('-checkInDate')[:1].annotate(date=F('checkInDate__date'))
      return hike


class CreateTrail(graphene.Mutation):
   trail = graphene.Field(TrailType) 

   class Arguments:
      name = graphene.String(required=True) 
      prop = graphene.String(required=True) 
      city = graphene.String(required=True)
      state = graphene.String(required=True) 
      description = graphene.String(required=True) 
      isOpen = graphene.Boolean(required=True) 
      altitudeChange = graphene.Int(required=True) 
      distance = graphene.Int(required=True) 
      fee = graphene.Float(required=True)

   def mutate(self, info, name, prop, city, state, description, isOpen, altitudeChange, distance, fee):
      trail = Trail(name=name, prop=prop, city=city, state=state, description=description, isOpen=isOpen, altitudeChange=altitudeChange, distance=distance, fee=fee)
      trail.save()
      return CreateTrail(trail=trail)

class CheckIn(graphene.Mutation):
   hike = graphene.Field(HikeType)
   date = graphene.Date()

   class Arguments:
      trailID = graphene.Int(required=True)
      hikerID = graphene.Int()

   # def mutate(self, info, trailID, hikerID):
   #    trail = Trail.objects.get(id=trailID)
   #    hiker = Hiker.objects.get(id=hikerID)
   #    hike = Hike(trail=trail, hiker=hiker)
   #    hike.save()
   #    return CheckIn(hike=hike)

   def mutate(self, info, trailID, **kwargs):
      trail = Trail.objects.get(id=trailID)
      hikerID = kwargs.get('hikerID', None)
      if hikerID:
         hiker = Hiker.objects.get(id=hikerID)
      else:
         user = info.context.user 
         if user.is_anonymous:
            raise Exception("Not logged in.")
         hiker = Hiker.objects.get(user=user)
      hike = Hike(trail=trail, hiker=hiker)
      hike.save()
      return CheckIn(hike=hike, date=hike.checkInDate.date())


class LeaveReview(graphene.Mutation):
   hike = graphene.Field(HikeType)

   class Arguments:
      hikeID = graphene.Int(required=True)
      review = graphene.String()
      difficulty = graphene.Int()
      enjoyability = graphene.Int()

   def mutate(self, info, hikeID, review, difficulty, enjoyability):
      hike = Hike.objects.get(id=hikeID)
      hike.review = review
      hike.difficulty = difficulty 
      hike.enjoyability = enjoyability
      hike.save()
      return LeaveReview(hike=hike)

class CheckOut(graphene.Mutation):
   hike = graphene.Field(HikeType)

   class Arguments:
      hikeID = graphene.Int()
      trailID = graphene.Int(required=True)

   def mutate(self, info, trailID, **kwargs):
      hikeID = kwargs.get('hikeID', None)
      hike = None
      if hikeID:
         hike = Hike.objects.get(id=hikeID)
      else: 
         user = info.context.user
         if user.is_anonymous:
            raise Exception('Not logged in')
         hiker = Hiker.objects.get(user=user)
         trail = Trail.objects.get(id=trailID)
         hike = Hike.objects.filter(hiker=hiker, trail=trail).order_by('-checkInDate')[0]
      hike.checkOutDate = datetime.now()
      hike.save()
      return CheckOut(hike=hike)

class AddBuddy(graphene.Mutation):
   buddy = graphene.Field(BuddyType)

   class Arguments:
      hikeID = graphene.Int(required=True)
      friendID = graphene.Int(required=True)

   def mutate(self, info, hikeID, friendID):
      hike = Hike.objects.get(id=hikeID)
      friend = Hiker.objects.get(id=friendID)
      buddy = Buddy(friendID=friend, hikeID=hike)
      buddy.save()
      return AddBuddy(buddy=buddy)

class CreateSuggestedEquipment(graphene.Mutation): 
   suggestedEquipment = graphene.Field(SuggestedEquipmentType)

   class Arguments:
      trailID = graphene.Int(required=True) 
      equTypeID = graphene.Int(required=True) 

   def mutate(self, info, trailID, equTypeID):
      trail = Trail.objects.get(id=trailID)
      equType = EquipmentType.objects.get(id=equTypeID)
      suggestedEquipment = SuggestedEquipment(trailID=trail, equipmentTypeID=equType)
      suggestedEquipment.save()
      return CreateSuggestedEquipment(suggestedEquipment=suggestedEquipment)

class AddEquipmentUsed(graphene.Mutation):
   equipmentUsed = graphene.Field(EquipmentUsedType)

   class Arguments:
      hikeID = graphene.Int(required=True)
      equTypeID = graphene.Int(required=True)

   def mutate(self, info, hikeID, equTypeID):
      hike = Hike.objects.get(id=hikeID)
      equType = EquipmentType.objects.get(id=equTypeID)
      equipmentUsed = EquipmentUsed(hikeID=hike, equipmentID=equType)
      equipmentUsed.save()
      return AddEquipmentUsed(equipmentUsed=equipmentUsed)

class CreateTag(graphene.Mutation):
   tag = graphene.Field(TagType)

   class Arguments:
      trailID = graphene.Int(required=True) 
      tag = graphene.String(required=True) 

   def mutate(self, info, trailID, tag):
      trail = Trail.objects.get(id=trailID)
      tag = Tag(trailID=trail, tag=tag)
      tag.save()
      return CreateTag(tag=tag)

class AddFriend(graphene.Mutation):
   friend = graphene.Field(FriendType)

   class Arguments:
      hikerID = graphene.Int(required=True)
      friendID = graphene.Int(required=True)

   def mutate(self, info, hikerID, friendID):
      hiker = Hiker.objects.get(id=hikerID)
      friend = Hiker.objects.get(id=friendID)
      friendListing = Friend(hikerID=hiker, friendID=friend, friendedBack=False)
      friendListing.save()
      return AddFriend(friend=friendListing)

class SendMessage(graphene.Mutation):
   message = graphene.Field(MessageType)

   class Arguments:
      hikerID = graphene.Int(required=True)
      recipientID = graphene.Int(required=True)
      content = graphene.String(required=True)

   def mutate(self, info, hikerID, recipientID, content):
      hikerID = Hiker.objects.get(id=hikerID)
      recipientID = Hiker.objects.get(id=recipientID)
      message = Message(hikerID=hikerID, recipientID=recipientID, content=content)
      message.save()
      return SendMessage(message=message)

class CreateEquipmentType(graphene.Mutation):
   equipmentType = graphene.Field(EquipmentTypeType)

   class Arguments:
      equType = graphene.String(required=True) 

   def mutate(self, info, equType):
      equipmentType = EquipmentType(equType=equType)
      equipmentType.save()
      return CreateEquipmentType(equipmentType=equipmentType)

################################ vvvvvvvvvvvvvv TESTING: POPULATE TABLES vvvvvvvvvvvvvvv ##############################################
class PopTrail(graphene.Mutation):
   trail = graphene.Field(TrailType) 

   class Arguments:
      name = graphene.String() 
      prop = graphene.String() 
      city = graphene.String()
      state = graphene.String() 
      description = graphene.String() 
      isOpen = graphene.Boolean() 
      altitudeChange = graphene.Int() 
      distance = graphene.Int() 
      fee = graphene.Float()

   def mutate(self, info):
      count = Trail.objects.all().count()
      name = "name" + str(count+1)
      prop = "prop" + str(count+1)
      city = "city" + str(count+1)
      state = "state" + str(count+1)
      description = "description" + str(count+1)
      isOpen = True 
      altitudeChange = 1000
      distance = 5000 
      fee = 1.5
      trail = Trail(name=name, prop=prop, city=city, state=state, description=description, isOpen=isOpen, altitudeChange=altitudeChange, distance=distance, fee=fee)
      trail.save()
      return CreateTrail(trail=trail)


################################ ^^^^^^^^^^^^^^^ TESTING: POPULATE TABLES ^^^^^^^^^^^^^^^^ ##############################################


class Mutation(graphene.ObjectType):
   create_trail = CreateTrail.Field()
   check_in = CheckIn.Field()
   check_out = CheckOut.Field()
   leave_review = LeaveReview.Field()
   create_suggested_equipment = CreateSuggestedEquipment.Field()
   create_tag = CreateTag.Field()
   add_friend = AddFriend.Field()
   send_message= SendMessage.Field()
   create_equipment_type = CreateEquipmentType.Field()
   add_buddy = AddBuddy.Field()
   add_equipment_used = AddEquipmentUsed.Field()

   ############ vvvvvvv TESTING: POPULATE TABLES vvvvvv ###########
   pop_trail = PopTrail.Field()