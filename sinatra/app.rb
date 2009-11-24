#! /usr/bin/ruby
require 'rubygems'
require 'sinatra'

get '/stylesheets/screen.css' do
  header 'Content-Type' => 'text/css; charset=utf-8'
   sass :stylesheet, :sass_options => {:style => :expanded } # overridden
end

get '/' do
  haml :index
end

post '/' do
  # create a form
end

put '/' do
  #update a form
end

delete '/' do
  #delete a form
end
